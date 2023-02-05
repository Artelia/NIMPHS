# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import IntProperty, EnumProperty, StringProperty, PointerProperty, FloatProperty

import logging
log = logging.getLogger(__name__)

import os
import time
import json
import tempfile
import numpy as np
from pathlib import Path

from nimphs.operators.shared.utils import update_end
from nimphs.panels.utils import get_selected_object, draw_point_data
from nimphs.operators.shared.modal_operator import NIMPHS_ModalOperator
from nimphs.operators.shared.create_sequence import NIMPHS_CreateSequence
from nimphs.check_dependencies import HAS_CUDA, HAS_MULTIPROCESSING, HAS_PYOPENVDB
from nimphs.operators.utils.volume import TelemacMeshForVolume, TelemacVolume
from nimphs.properties.telemac.interpolate import NIMPHS_TelemacInterpolateProperty
from nimphs.properties.utils.point_data import PointDataInformation, PointDataManager


def get_available_computing_modes(self, _context: Context) -> list:  # noqa: D417
    """
    Return available computing modes for volume computation of TELEMAC 3D files.

    Args:
        _context (Context): context

    Returns:
        list: list of available computing modes
    """

    items = [("DEFAULT", "Default", "Default mode, can be very slow for large dimensions")]
    if HAS_MULTIPROCESSING:
        items.append(("MULTIPROCESSING", "Multiprocessing", "Multiprocessing mode, can speed up a lot the computation"))
    if HAS_CUDA:
        items.append(("CUDA", "CUDA", "CUDA mode, can dramatically improve the computation speed"))

    return items


def update_nb_threads(self, _context: Context) -> None:  # noqa: D417
    """
    Update the number of chosen cpu threads in function of the computing capabilities.

    Args:
        _context (Context): context
    """

    value = self["nb_threads"]
    cpu_count = len(os.sched_getaffinity(0))

    if value > cpu_count:
        self["nb_threads"] = cpu_count
    elif value < 2:
        value = 2


def update_dim_x(self, context: Context) -> None:  # noqa: D417
    """
    Update volume X dimension accordingly to the model's dimensions.

    Args:
        _context (Context): context
    """

    file_data = context.scene.nimphs.file_data["ops"]
    ratio = file_data.dimensions[0] / file_data.dimensions[1]

    # Adjust Y dimension to new X dimension
    # Also adjust voxel size
    if ratio > 1.0:
        self["dim_y"] = int(np.ceil(self.get("dim_x") / ratio))
        self["vx_size"] = file_data.dimensions[0] / self.get("dim_x")
    else:
        self["dim_y"] = int(np.ceil(self.get("dim_x") * ratio))
        self["vx_size"] = file_data.dimensions[1] / self.get("dim_y")


def update_dim_y(self, context: Context) -> None:  # noqa: D417
    """
    Update volume Y dimension accordingly to the model's dimensions.

    Args:
        _context (Context): context
    """

    file_data = context.scene.nimphs.file_data["ops"]
    ratio = file_data.dimensions[0] / file_data.dimensions[1]

    # Adjust X dimension to new Y dimension
    # Also adjust voxel size
    if ratio < 1.0:
        self["dim_x"] = int(np.ceil(self.get("dim_y") / ratio))
        self["vx_size"] = file_data.dimensions[1] / self.get("dim_y")
    else:
        self["dim_x"] = int(np.ceil(self.get("dim_y") * ratio))
        self["vx_size"] = file_data.dimensions[0] / self.get("dim_x")


def update_vx_size(self, context: Context) -> None:  # noqa: D417
    """
    Update dimensions according to new voxel size.

    Args:
        _context (Context): context
    """

    file_data = context.scene.nimphs.file_data["ops"]
    self["dim_x"] = int(np.ceil(file_data.dimensions[0] / self.get("vx_size")))
    self["dim_y"] = int(np.ceil(file_data.dimensions[1] / self.get("vx_size")))


class NIMPHS_OT_TelemacGenerateVolumeSequence(NIMPHS_CreateSequence, NIMPHS_ModalOperator):
    """Operator to generate volume sequences from TELEMAC 3D objects."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.telemac_generate_volume_sequence"
    bl_label = "Volume sequence"
    bl_description = "Generate a volume sequence from a TELEMAC 3D file. Press 'esc' to cancel"

    #: bpy.props.EnumProperty: Computing mode. Enum in ['DEFAULT', 'MULTIPROCESSING', 'CUDA'].
    computing_mode: EnumProperty(
        name="Computing mode",
        description="Select a computing method from a list of available computing modes",
        items=get_available_computing_modes
    )

    #: bpy.props.IntProperty: Number of threads to use when multiprocessing mode is chosen.
    nb_threads: IntProperty(
        name="Number of threads",
        description="Number of threads to use in case the multiprocessing computing method is chosen",
        default=2,
        soft_min=2,
        min=2,
        update=update_nb_threads
    )

    #: bpy.props.StringProperty: Output path for generated .vdb files.
    output_path: StringProperty(
        name="Output path",
        description="Path where to save generated .vdb files",
        default="",
        subtype="DIR_PATH"      # noqa: F821
    )

    #: bpy.props.StringProperty: File name of generated .vdb files.
    file_name: StringProperty(
        name="Output path",
        description="Name of the files to generate",
        default="",
        subtype="FILE_NAME"     # noqa: F821
    )

    #: bpy.props.EnumProperty: Indicate how the volume is defined.
    volume_definition: EnumProperty(
        name="Volume definition",
        description="Define the volume dimensions either by providing dimensions or a voxel size",
        items=[
            ("DIMENSIONS", "Dimensions", "Define the volume by giving custom dimensions (L x W x H)"),  # noqa: F821
            ("VX_SIZE", "Voxel size", "Define the volume using a voxel size"),                          # noqa: F821
        ]
    )

    #: bpy.props.IntProperty: Volume dimension along the 'X' axis.
    dim_x: IntProperty(
        name="X dimension",
        default=0,
        min=1,
        soft_min=1,
        update=update_dim_x
    )

    #: bpy.props.IntProperty: Volume dimension along the 'Y' axis.
    dim_y: IntProperty(
        name="Y dimension",
        default=0,
        min=1,
        soft_min=1,
        update=update_dim_y
    )

    #: bpy.props.IntProperty: Volume dimension along the 'Z' axis.
    dim_z: IntProperty(
        name="Z dimension",
        default=0,
        min=1,
        soft_min=1,
    )

    #: bpy.props.IntProperty: Voxel size.
    vx_size: FloatProperty(
        name="Voxel size",
        description="Size of a voxel",
        default=0.0,
        min=1e-6,
        soft_min=1e-6,
        precision=6,
        update=update_vx_size
    )

    #: bpy.props.IntProperty: Ending frame / time point of the sequence.
    end: IntProperty(
        name="End",  # noqa: F821
        description="Ending frame / time point of the sequence",
        default=1,
        update=update_end,
        soft_min=0,
        min=0
    )

    #: NIMPHS_TelemacInterpolateProperty: Time interpolation settings.
    time_interpolation: PointerProperty(type=NIMPHS_TelemacInterpolateProperty)

    #: NIMPHS_TelemacInterpolateProperty: Space interpolation settings.
    space_interpolation: PointerProperty(type=NIMPHS_TelemacInterpolateProperty)

    #: int: Currently processed time point
    time_point: int = 0

    #: int: File counter to give a unique name to generated files
    file_counter: int = 0

    #: float: Cumulated execution time of the operator
    cumulated_time: float = 0

    #: TelemacMeshForVolume: Mesh information for the generation of TELEMAC volumes
    mesh: TelemacMeshForVolume = None

    #: TelemacVolume: Object which will handle the computation of volumes
    volume: TelemacVolume = None

    #: float: Z dimension of voxel size
    vx_size_z: float = 0.0

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        if super().poll(context):
            obj = get_selected_object(context)
        else:
            return False

        return obj.nimphs.module == 'TELEMAC'

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        if not HAS_PYOPENVDB:
            self.report({'WARNING'}, "Python package unavailable: pyopenvdb")
            return {'CANCELLED'}

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        file_data = context.scene.nimphs.file_data.get(self.obj.nimphs.uid, None)
        if file_data is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        if not file_data.is_3d():
            self.report({'WARNING'}, "Selected object is not a TELEMAC 3D model")
            return {'CANCELLED'}

        # Clear selected point data
        context.scene.nimphs.op_vars.clear()
        # Limit point data import to 1
        self.limit_add_point_data = 1
        # "Copy" file data
        context.scene.nimphs.file_data["ops"] = context.scene.nimphs.file_data[self.obj.nimphs.uid]
        self.max = context.scene.nimphs.file_data["ops"].nb_time_points - 1

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            # Read test data
            data = json.loads(self.test_data)

            point_data = PointDataManager()
            point_data.append(name=data.get("point_data", None))
            self.point_data.list = point_data.dumps()

            self.max = data.get("max", 0)
            self.start = data.get("start", 0)
            self.end = data.get("end", 0)

            self.output_path = os.path.abspath(data.get("output_path", "/tmp"))
            self.file_name = data.get("file_name", "DEFAULT_FILE_NAME_VOLUME")

            self.computing_mode = data.get("computing_mode", "DEFAULT")
            self.nb_threads = data.get("nb_threads", 4)

            self.volume_definition = 'DIMENSIONS'
            self.dim_x = data.get("dim_x", 0)
            self.dim_y = data.get("dim_y", 0)
            self.dim_z = data.get("dim_z", 0)

            self.time_interpolation.type = 'LINEAR'
            self.time_interpolation.steps = data.get("time_interpolation", 1)

            self.space_interpolation.type = 'LINEAR'
            self.space_interpolation.steps = data.get("space_interpolation", 1)

            return {'FINISHED'}
        else:
            self.file_name = "Volume_sequence"
            self.output_path = os.path.abspath(tempfile.gettempdir())

            # Compute default dimensions
            dim = context.scene.nimphs.file_data["ops"].dimensions
            # om = order of magnitude
            omx, omy, omz = int(np.log10(dim[0])), int(np.log10(dim[1])), int(np.log10(dim[2]))
            raw = (
                dim[0] / pow(10, omx - 2) if omx > 2 else dim[0],
                dim[1] / pow(10, omy - 2) if omy > 2 else dim[1],
                dim[2] / pow(10, omz - 2) if omz > 2 else dim[2]
            )
            dim_x = int(np.ceil(raw[0]))
            dim_y = int(np.ceil(raw[1]))
            self.dim_z = int(np.ceil(raw[2]))

            if self.dim_x > self.dim_z:
                self.vx_size = dim[0] / dim_x
            else:
                self.vx_size = dim[1] / dim_y

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window.

        Args:
            context (Context): context
        """

        file_data = context.scene.nimphs.file_data["ops"]

        # Hardware
        box = self.layout.box()
        row = box.row()
        row.label(text="Hardware")

        row = box.row()
        row.prop(self, "computing_mode", text="Mode")

        if self.computing_mode == 'MULTIPROCESSING':
            row = box.row()
            row.prop(self, "nb_threads", text="Number of threads")

        # Volume settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Volume")

        subbox = box.box()
        row = subbox.row()
        row.label(text="Size")

        row = subbox.row()
        row.prop(self, "volume_definition", text="Volume definition")

        if self.volume_definition == 'VX_SIZE':
            row = subbox.row()
            row.prop(self, "vx_size", text="Voxel size")
        elif self.volume_definition == 'DIMENSIONS':
            row = subbox.row()
            row.prop(self, "dim_x", text="")
            row.prop(self, "dim_y", text="")
            row.prop(self, "dim_z", text="")

        row = subbox.row()
        row.label(text=f"Total voxels: {self.dim_x * self.dim_y * self.dim_z}")
        row = subbox.row()
        xy = round(self.vx_size, 3)
        self.vx_size_z = round(file_data.dimensions[2] / self.dim_z, 3)
        row.label(text=f"Voxel dimensions: {xy} x {xy} x {self.vx_size_z}")

        subbox = box.box()
        row = subbox.row()
        row.label(text="Density")

        # Update list of chosen point data from this operator. Ugly but it works.
        self.point_data.list = context.scene.nimphs.op_vars.dumps()
        draw_point_data(subbox, self.point_data, show_remap=False, edit=True, src='OPERATOR')

        row = subbox.row()
        row.enabled = context.scene.nimphs.op_vars.length() < self.limit_add_point_data
        op = row.operator("nimphs.add_point_data", text="Add", icon='ADD')
        op.available = file_data.vars.dumps()
        op.chosen = self.point_data.list
        op.source = 'OPERATOR'

        # Interpolation settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Interpolation")

        # Space interpolation
        subbox = box.box()
        row = subbox.row()
        row.label(text="Space (generate interpolated planes between each known planes)")

        row = subbox.row()
        row.prop(self.space_interpolation, "type", text="Type")

        if self.space_interpolation.type != 'NONE':
            row = subbox.row()
            row.prop(self.space_interpolation, "steps", text="Steps")

        # Time interpolation
        subbox = box.box()
        row = subbox.row()
        row.label(text="Time (generate interpolated time steps)")

        row = subbox.row()
        row.prop(self.time_interpolation, "type", text="Type")

        if self.time_interpolation.type != 'NONE':
            row = subbox.row()
            row.prop(self.time_interpolation, "steps", text="Steps")

        # Sequence
        box = self.layout.box()
        row = box.row()
        row.label(text="Sequence")

        row = box.row()
        row.prop(self, "output_path", text="Output directory")
        row = box.row()
        row.prop(self, "file_name", text="File name")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "end", text="End")

    def execute(self, context: Context) -> set:
        """
        Prepare the execution of the 'create mesh sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            self.invoke(context, None)

        # Check destination path
        path = Path(self.output_path)
        if not path.exists():
            self.report({'WARNING'}, "Given output path does not exists")
            return {'CANCELLED'}

        start = time.time()

        self.cumulated_time = 0.0
        self.file_counter = self.start
        self.time_point = self.start - 1 if self.mode != 'TEST' else self.start
        # Concatenate output_path and file_name
        self.file_name = os.path.join(os.path.abspath(self.output_path), self.file_name)

        point_data = json.loads(self.point_data.list)
        if len(point_data["names"]) <= 0:
            self.report({'WARNING'}, "No point data selected")
            return {'CANCELLED'}

        prefs = context.preferences.addons["nimphs"].preferences.settings

        try:
            # Setup mesh information for volume
            self.mesh = TelemacMeshForVolume(
                self.obj.nimphs.settings.file_path,
                self.space_interpolation.steps if self.space_interpolation.type != 'NONE' else 0,
                self.time_interpolation.steps if self.time_interpolation.type != 'NONE' else 0
            )

            # Setup volume
            if self.volume_definition == 'VX_SIZE':
                self.volume = TelemacVolume(self.mesh, self.nb_threads, self.computing_mode == 'MULTIPROCESSING',
                                            self.computing_mode == 'CUDA',
                                            vx_size=(self.vx_size, self.vx_size, self.vx_size_z),
                                            show_details=prefs.log_level == 'DEBUG')

            if self.volume_definition == 'DIMENSIONS':
                self.volume = TelemacVolume(self.mesh, self.nb_threads, self.computing_mode == 'MULTIPROCESSING',
                                            self.computing_mode == 'CUDA',
                                            dimensions=(self.dim_x, self.dim_y, self.dim_z),
                                            show_details=prefs.log_level == 'DEBUG')
        except BaseException:
            log.error("Error when generating volume", exc_info=1)
            self.report({'ERROR'}, "Error when generating volume")
            return {'CANCELLED'}

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            # Prepare volume ------
            self.volume.prepare_voxels(self.mesh)

            # Generate volume -----
            while self.time_point <= self.end:
                # Update data
                self.mesh.set_time_point(self.time_point)

                # Get variable information
                variable: PointDataInformation = PointDataManager(self.point_data.list).get(0)
                var_name = variable.name

                # Export volume at current time point
                self.volume.export_time_point(self.mesh, [var_name], f"{self.file_name}_{self.file_counter}")
                self.file_counter += 1

                # Generate interpolated time steps
                if self.time_point < self.end:
                    for interp_time_point in range(1, self.mesh.time_interp_steps + 1):
                        self.mesh.set_time_point(self.time_point, interp_time_point)
                        self.volume.export_time_point(self.mesh, [var_name],
                                                      f"{self.file_name}_{self.file_counter}")
                        self.file_counter += 1

                self.time_point += 1

            return {'FINISHED'}
        else:
            # Setup progress bar + force to display (set a new value)
            super().prepare(context, "Preparing volume...")
            super().set_progress(context, 0.0)

            self.cumulated_time += time.time() - start

            return {'RUNNING_MODAL'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'generate_volume_sequence' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event.type == 'ESC':
            super().stop(context, canceled=True)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.time_point == self.start - 1:

                start = time.time()

                try:
                    # Prepare volume
                    self.volume.prepare_voxels(self.mesh)
                except BaseException:
                    super().stop(context)
                    log.debug("Error when preparing voxels", exc_info=1)
                    self.report({'ERROR'}, "Error when preparing voxels")
                    return {'CANCELLED'}

                if self.volume.show_details:
                    log.debug(f"Total: {time.time() - start}s")

                self.time_point += 1
                super().update_label(context, "Computing volume...")
                self.cumulated_time += time.time() - start

                return {'PASS_THROUGH'}

            if self.time_point <= self.end:

                start_tp = time.time()

                try:

                    # Update data
                    start = time.time()
                    self.mesh.set_time_point(self.time_point)
                    if self.volume.show_details:
                        log.debug(f"Set time point: {time.time() - start}s")

                    # Get variable information
                    variable: PointDataInformation = PointDataManager(self.point_data.list).get(0)
                    var_name = variable.name

                    # Export volume at current time point
                    self.volume.export_time_point(self.mesh, [var_name], f"{self.file_name}_{self.file_counter}")
                    self.file_counter += 1

                    # Generate interpolated time steps
                    if self.time_point < self.end:
                        for interp_time_point in range(1, self.mesh.time_interp_steps + 1):
                            self.mesh.set_time_point(self.time_point, interp_time_point)
                            self.volume.export_time_point(self.mesh, [var_name],
                                                          f"{self.file_name}_{self.file_counter}")
                            self.file_counter += 1

                except BaseException:
                    super().stop(context)
                    self.report({'ERROR'}, f"Error when processing time point {self.time_point}")
                    return {'CANCELLED'}

                if self.volume.show_details:
                    log.debug(f"Time point {self.time_point}: {time.time() - start_tp}s")

                self.cumulated_time += time.time() - start_tp

            else:
                super().stop(context)
                log.debug(f"Cumulated time: {self.cumulated_time}")
                self.report({'INFO'}, f"Generate volume sequence finished ({np.ceil(self.cumulated_time)}s)")
                return {'FINISHED'}

            # Update the progress bar
            super().update_progress(context, self.time_point - self.start, (self.end - self.start) + 1)
            self.time_point += 1

        return {'PASS_THROUGH'}
