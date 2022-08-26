# <pep8 compliant>
from bpy.types import Operator, Context, Event, Object
from bpy.props import EnumProperty, IntProperty, StringProperty

import logging
log = logging.getLogger(__name__)

from nimphs.panels.utils import get_selected_object
from nimphs.properties.utils.point_data import PointDataManager
from nimphs.properties.utils.properties import available_point_data
from nimphs.operators.shared.modal_operator import NIMPHS_ModalOperator
from nimphs.operators.shared.utils import update_end, update_plane_id, update_start


class NIMPHS_OT_TelemacExtractPointData(Operator, NIMPHS_ModalOperator):
    """Operator to extract point data from a TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.telemac_extract_point_data"
    bl_label = "Extract point data"
    bl_description = "Extract point data from a TELEMAC object"

    #: int: Time point currently processed.
    time_point: int = 0

    #: int: Current frame during the process (different from time point).
    frame: int = 0

    #: bpy.types.Object: Selected object
    obj: Object = None

    #: bpy.props.IntProperty: Index of the vertex from which extract data.
    vertex_id: IntProperty(
        name="Vertex id",
        description="Index of the vertex from which extract data",
        default=0,
        soft_min=0,
        min=0,
    )

    #: bpy.props.EnumProperty: Point data to extract.
    point_data: EnumProperty(
        name="Point data",
        description="Point data to extract",
        items=available_point_data,
    )

    #: bpy.props.StringProperty: Name of the chosen variable to extract.
    chosen_variable: StringProperty(
        name="Chosen variable",
        description="Name of the chosen variable to extract",
        default="",
        options={'HIDDEN'}  # noqa: F821
    )

    #: bpy.props.IntProperty: Index of the plane on which the vertex is located.
    plane_id: IntProperty(
        name="Plane",  # noqa: F821
        description="Index of the plane on which the vertex is located",
        default=0,
        update=update_plane_id,
        soft_min=0,
        min=0,
    )

    #: bpy.props.IntProperty: Highest available plane id.
    max_plane_id: IntProperty(
        name="Plane",  # noqa: F821
        description="Highest available plane id",
        default=0,
        soft_min=0,
        min=0,
        options={'HIDDEN'}  # noqa: F821
    )

    #: bpy.props.IntProperty: Number of maximum available time points to extract.
    max: IntProperty(
        name="Max",  # noqa: F821
        description="Number of maximum available time points to extract",
        default=1,
        options={'HIDDEN'},  # noqa: F821
    )

    #: bpy.props.IntProperty: Start time point.
    start: IntProperty(
        name="Start",  # noqa: F821
        description="Start time point",
        update=update_start,
        default=0,
        soft_min=0,
        min=0,
    )

    #: bpy.props.IntProperty: End time point.
    end: IntProperty(
        name="Start",  # noqa: F821
        description="Start time point",
        update=update_end,
        default=0,
        soft_min=0,
        min=0,
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.nimphs.module == 'TELEMAC'
        else:
            return False

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

        if context.scene.nimphs.file_data.get(self.obj.nimphs.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # "Copy" file data
        context.scene.nimphs.file_data["ops"] = context.scene.nimphs.file_data[self.obj.nimphs.uid]
        file_data = context.scene.nimphs.file_data["ops"]

        # Set 'max' settings
        if file_data.is_3d():
            self.max_plane_id = file_data.nb_planes - 1
        self.max = file_data.nb_time_points - 1

        # Set default target object
        context.scene.nimphs.op_target = self.obj

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            return {'FINISHED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        file_data = context.scene.nimphs.file_data.get("ops", None)

        if file_data is not None:
            # Extract settings
            box = self.layout.box()
            row = box.row()
            row.label(text="Extract")

            row = box.row()
            row.prop(self, "vertex_id", text="Vertex ID")

            if file_data.is_3d():
                row = box.row()
                row.prop(self, "plane_id", text="Plane id")

            row = box.row()
            row.prop(self, "point_data", text="Point data")
            row = box.row()
            row.prop_search(context.scene.nimphs, "op_target", context.scene, "objects", text="Target")

            # Time related settings
            box = self.layout.box()
            row = box.row()
            row.label(text="Time")

            row = box.row()
            row.prop(self, "start", text="Start")
            row = box.row()
            row.prop(self, "end", text="End")

    def execute(self, context: Context) -> set:
        """
        Extract point data.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Setup operator settings
        self.frame = 0
        self.time_point = self.start

        if self.mode == 'MODAL':
            self.chosen_variable = PointDataManager(self.point_data).get(0, prop='NAME')
            super().prepare(context, "Extracting...")
            return {'RUNNING_MODAL'}

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            self.invoke(context, None)
            self.chosen_variable = PointDataManager(self.test_data).get(0, prop='NAME')

            while self.time_point <= self.end:

                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    return state

                self.time_point += 1
                self.frame += 1

            return {'FINISHED'}

        return {'CANCELLED'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'extract point data' process.

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
            if self.time_point <= self.end:
                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    super().stop(context)
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Extracting completed")
                return {'FINISHED'}

            # Update the progress bar
            super().update_progress(context, self.time_point, self.end + 1)
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the process.

        Args:
            context (Context): context

        Returns:
            set: state of the operation. Enum in ['PASS_THROUGH', 'CANCELLED'].
        """

        # Get and update file data
        file_data = context.scene.nimphs.file_data["ops"]
        file_data.update_data(self.time_point)

        # Get value of the selected vertex
        value = file_data.get_point_data(self.chosen_variable)[self.vertex_id + file_data.nb_vertices * self.plane_id]

        # Insert new keyframe in custom property
        context.scene.nimphs.op_target[self.chosen_variable] = value
        context.scene.nimphs.op_target.keyframe_insert(data_path=f'["{self.chosen_variable}"]', frame=self.frame)

        return {'PASS_THROUGH'}
