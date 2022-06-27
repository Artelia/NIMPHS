# <pep8 compliant>
from bpy.types import Operator, Context, Event, Object
from bpy.props import EnumProperty, IntProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.utils import VariablesInformation, available_point_data
from tbb.operators.shared.utils import update_end, update_start
from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings
from tbb.operators.shared.modal_operator import TBB_ModalOperator


class TBB_OT_TelemacExtractPointData(Operator, TBB_ModalOperator):
    """Operator to extract point data from a TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_extract_point_data"
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

    #: bpy.props.EnumProperty: Point data to extract data.
    point_data: EnumProperty(
        name="Point data",
        description="Point data to extract",
        items=available_point_data,
    )

    #: bpy.props.IntProperty: Number of maximum available time points to extract.
    max: IntProperty(
        name="Max",
        description="Number of maximum available time points to extract",
        default=1,
    )

    #: bpy.props.IntProperty: Start time point.
    start: IntProperty(
        name="Start",
        description="Start time point",
        update=update_start,
        default=0,
        soft_min=0,
        min=0,
    )

    #: bpy.props.IntProperty: End time point.
    end: IntProperty(
        name="Start",
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
            return obj.tbb.module == 'TELEMAC'
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

        if context.scene.tbb.file_data.get(self.obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # "Copy" file data
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[self.obj.tbb.uid]
        self.max = context.scene.tbb.file_data["ops"].nb_time_points
        # Set default target
        context.scene.tbb.op_target = self.obj

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        # Extract settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Extract")

        row = box.row()
        row.prop(self, "vertex_id", text="Vertex ID")
        row = box.row()
        row.prop(self, "point_data", text="Point data")
        row = box.row()
        row.prop_search(context.scene.tbb, "op_target", context.scene, "objects", text="Target")

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

        # Setup time settings
        self.time_point = self.start
        self.frame = 0

        if self.mode == 'MODAL':
            super().prepare(context, "Extracting...")
            return {'RUNNING_MODAL'}

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
            super().stop(context, cancelled=True)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.time_point <= self.end:
                # Get and update file data
                file_data = context.scene.tbb.file_data["ops"]
                file_data.update_data(self.time_point)

                # Get value of the selected vertex
                data_name = VariablesInformation(self.point_data).get(0, 'NAME')
                value = file_data.get_point_data(data_name)[self.vertex_id]

                # Insert new keyframe in custom property
                self.obj.tbb.extracted_point_data = value
                self.obj.tbb.keyframe_insert(data_path="extracted_point_data", frame=self.frame)

            else:
                super().stop(context)
                self.report({'INFO'}, "Extracting completed")
                return {'FINISHED'}

            # Update the progress bar
            super().update_progress(context, self.time_point, self.end)
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}
