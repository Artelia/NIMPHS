# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.operators.shared.modal_operator import TBB_ModalOperator
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class TBB_OT_ComputeRangesPointDataValues(Operator, TBB_ModalOperator):
    """Operator to compute ranges of point data values."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.compute_ranges_point_data_values"
    bl_label = "Compute ranges of point data values"
    bl_description = "Compute ranges of point data values"

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        csir = context.scene.tbb.m_op_running  # csir = create sequence is running
        obj = get_selected_object(context)
        if obj is None:
            return False

        return obj.tbb.module in ['OpenFOAM', 'TELEMAC'] and not csir

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None:
            return {'CANCELLED'}

        if context.scene.tbb.file_data.get(obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # "Copy" file data information
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[obj.tbb.uid]
        self.max_length = context.scene.tbb.file_data["ops"].nb_time_points

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        file_data = context.scene.tbb.file_data["ops"]

        # Import point data
        box = self.layout.box()
        row = box.row()
        row.label(text="Variables")

        # Update list of chosen point data from this operator. Ugly but it works.
        self.point_data.list = context.scene.tbb.op_vars.dumps()

        draw_point_data(box, self.point_data, show_remap=False, show_range=False, edit=True, src='OPERATOR')

        row = box.row()
        op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
        op.available = file_data.vars.dumps()
        op.chosen = self.point_data.list
        op.source = 'OPERATOR'

    def execute(self, context: Context) -> set:
        """
        Compute ranges of point data values ('GLOBAL' scope).

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        print("HELLO")
        return {'FINISHED'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'compute ranges of point data values' process.

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
                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Create sequence finished")
                return {'FINISHED'}

            # Update the progress bar
            context.scene.tbb.progress_value = self.time_point / (self.end - self.start)
            context.scene.tbb.progress_value *= 100
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}
