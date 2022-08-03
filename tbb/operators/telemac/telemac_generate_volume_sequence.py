# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import StringProperty, EnumProperty, IntProperty, IntVectorProperty, FloatVectorProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

import os
import time
import json
import tempfile
import numpy as np
from pathlib import Path

from tbb.operators.shared.utils import update_end
from tbb.checkdeps import HAS_CUDA, HAS_MULTIPROCESSING
from tbb.operators.shared.modal_operator import TBB_ModalOperator
from tbb.panels.utils import get_selected_object, draw_point_data
from tbb.operators.shared.create_sequence import TBB_CreateSequence
from tbb.operators.utils.volume import TelemacMeshForVolume, TelemacVolume
from tbb.properties.telemac.interpolate import TBB_TelemacInterpolateProperty
from tbb.properties.utils.point_data import PointDataInformation, PointDataManager


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


class TBB_OT_TelemacGenerateVolumeSequence(TBB_CreateSequence, TBB_ModalOperator):
    """Operator to generate volume sequences from TELEMAC 3D objects."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_generate_volume_sequence"
    bl_label = "Volume sequence"
    bl_description = "Generate a volume sequence from a TELEMAC 3D file. Press 'esc' to cancel"

    #: bpy.props.EnumProperty: Computing mode. Enum in ['DEFAULT', 'MULTIPROCESSING', 'CUDA']
    computing_mode: EnumProperty(
        name="Computing mode",
        description="Select a computing method from a list of available computing modes",
        items=get_available_computing_modes
    )

    nb_threads: IntProperty(
        name="Number of threads",
        description="Number of threads to use in case the multiprocessing computing method is chosen",
        default=2,
        soft_min=2,
        min=2,
        update=update_nb_threads
    )

    output_path: StringProperty(
        name="Output path",
        description="Path where to save generated .vdb files",
        default="",
        subtype="DIR_PATH"      # noqa: F821
    )

    file_name: StringProperty(
        name="Output path",
        description="Name of the files to generate",
        default="",
        subtype="FILE_NAME"     # noqa: F821
    )

    volume_definition: EnumProperty(
        name="Volume definition",
        description="Define the volume dimensions either by providing dimensions or a voxel size",
        items=[
            ("DIMENSIONS", "Dimensions", "Define the volume by giving custom dimensions (L x W x H)"),  # noqa: F821
            ("VX_SIZE", "Voxel size", "Define the volume using a voxel size"),                          # noqa: F821
        ]
    )

    dimensions: IntVectorProperty(
        name="Dimensions",  # noqa: F821
        description="Dimensions of the volume",
        default=(0, 0, 0),
        min=0,
        soft_min=0,
        size=3,
    )

    voxel_size: FloatVectorProperty(
        name="Voxel size",
        description="Size of a voxel",
        default=(0, 0, 0),
        min=0,
        soft_min=0,
        size=3,
        precision=3
    )

    time_interpolation: PointerProperty(type=TBB_TelemacInterpolateProperty)

    space_interpolation: PointerProperty(type=TBB_TelemacInterpolateProperty)

    #: bpy.props.IntProperty: Ending frame / time point of the sequence.
    end: IntProperty(
        name="End",  # noqa F821
        description="Ending frame / time point of the sequence",
        default=1,
        update=update_end,
        soft_min=0,
        min=0
    )

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

        return obj.tbb.module == 'TELEMAC'

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        if context.scene.tbb.file_data.get(self.obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # Clear selected point data
        context.scene.tbb.op_vars.clear()
        # Limit point data import to 1
        self.limit_add_point_data = 1
        # "Copy" file data
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[self.obj.tbb.uid]
        self.max = context.scene.tbb.file_data["ops"].nb_time_points - 1

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            return {'FINISHED'}
        else:
            self.file_name = "Volume_sequence"
            self.output_path = os.path.abspath(tempfile.gettempdir())

            # Compute default dimensions
            dim = context.scene.tbb.file_data["ops"].dimensions
            # om = order of magnitude
            omx, omy, omz = int(np.log10(dim[0])), int(np.log10(dim[1])), int(np.log10(dim[2]))
            raw = (
                dim[0] / pow(10, omx - 2) if omx > 2 else dim[0],
                dim[1] / pow(10, omy - 2) if omy > 2 else dim[1],
                dim[2] / pow(10, omz - 2) if omz > 2 else dim[2]
            )
            self.dimensions = (int(np.ceil(raw[0])), int(np.ceil(raw[1])), int(np.ceil(raw[2])))
            self.voxel_size = raw

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window.

        Args:
            context (Context): context
        """

        file_data = context.scene.tbb.file_data["ops"]

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
            row.prop(self, "voxel_size", text="Voxel size")
        elif self.volume_definition == 'DIMENSIONS':
            row = subbox.row()
            row.prop(self, "dimensions", text="Dimensions")

        subbox = box.box()
        row = subbox.row()
        row.label(text="Density")

        # Update list of chosen point data from this operator. Ugly but it works.
        self.point_data.list = context.scene.tbb.op_vars.dumps()
        draw_point_data(subbox, self.point_data, show_range=False, edit=True, src='OPERATOR')

        row = subbox.row()
        row.enabled = context.scene.tbb.op_vars.length() < self.limit_add_point_data
        op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
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

        # Check destination path
        path = Path(self.output_path)
        if not path.exists():
            self.report({'WARNING'}, "Given output path does not exists")
            return {'CANCELLED'}

        start = time.time()

        self.cumulated_time = 0.0
        self.file_counter = self.start
        self.time_point = self.start - 1
        # Concatenate output_path and file_name
        self.file_name = os.path.join(os.path.abspath(self.output_path), self.file_name)

        point_data = json.loads(self.point_data.list)
        if len(point_data["names"]) <= 0:
            self.report({'WARNING'}, "No point data selected to use as density")
            return {'CANCELLED'}

        try:
            # Setup mesh information for volume
            self.mesh = TelemacMeshForVolume(
                self.obj.tbb.settings.file_path,
                self.space_interpolation.steps if self.space_interpolation.type != 'NONE' else 0,
                self.time_interpolation.steps if self.time_interpolation.type != 'NONE' else 0
            )

            # Setup volume
            if self.volume_definition == 'VX_SIZE':
                self.volume = TelemacVolume(self.mesh, self.nb_threads, self.computing_mode == 'MULTIPROCESSING',
                                            self.computing_mode == 'CUDA', vx_size=self.voxel_size[0:3])

            if self.volume_definition == 'DIMENSIONS':
                self.volume = TelemacVolume(self.mesh, self.nb_threads, self.computing_mode == 'MULTIPROCESSING',
                                            self.computing_mode == 'CUDA', dimensions=self.dimensions[0:3])
        except BaseException:
            log.error("Error on generating volume", exc_info=1)
            self.report({'ERROR'}, "Error on generating volume")
            return {'CANCELLED'}

        # Setup progress bar + force to display (set a new value)
        super().prepare(context, "Prepare volume...")
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

            # Clear data
            self.mesh = None
            self.volume = None

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

                    if self.point_data.remap_method == 'LOCAL':
                        value_range = (variable.range.minL, variable.range.maxL)
                    elif self.point_data.remap_method == 'GLOBAL':
                        value_range = (variable.range.minG, variable.range.maxG)
                    elif self.point_data.remap_method == 'CUSTOM':
                        value_range = self.point_data.custom_remap_value[0:2]

                    # Export volume at current time point
                    self.volume.export_time_point(self.mesh, [var_name], f"{self.file_name}_{self.file_counter}",
                                                  remap=value_range)
                    self.file_counter += 1

                    # Generate interpolated time steps
                    if self.time_point < self.end:
                        for interp_time_point in range(1, self.mesh.time_interp_steps + 1):
                            self.mesh.set_time_point(self.time_point, interp_time_point)
                            self.volume.export_time_point(self.mesh, [var_name],
                                                          f"{self.file_name}_{self.file_counter}", remap=value_range)
                            self.file_counter += 1

                except BaseException:
                    super().stop(context)
                    self.report({'ERROR'}, "Error when updating time point")
                    return {'CANCELLED'}

                if self.volume.show_details:
                    log.debug(f"Total: {time.time() - start_tp}s")

                self.cumulated_time += time.time() - start_tp

            else:
                super().stop(context)
                self.report({'INFO'}, f"Generate volume sequence finished ({np.ceil(self.cumulated_time)}s)")
                return {'FINISHED'}

            # Update the progress bar
            super().update_progress(context, self.time_point - self.start, (self.end - self.start) + 1)
            self.time_point += 1

        return {'PASS_THROUGH'}
