# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty, PointerProperty

import logging
log = logging.getLogger(__name__)

from tbb.properties.utils import VariablesInformation
from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class TBB_OT_ComputeRangesPointDataValues(Operator):
    """Operator to compute ranges of point data values."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.compute_ranges_point_data_values"
    bl_label = "Point data value range"
    bl_description = "Compute ranges of point data values"

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: str: JSON strigified list of point data to import as vertex colors.
    list: str = VariablesInformation().dumps()

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        csir = context.scene.tbb.create_sequence_is_running  # csir = create sequence is running
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

        print(self.__class__.__name__)
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
        row.label(text="Point data")
        row = box.row()
        row.prop(self.point_data, "import_data", text="Import point data")

        if self.point_data.import_data:

            self.point_data.list = self.list
            draw_point_data(box, self.point_data, show_range=False, edit=True, src='OPERATOR')

            row = box.row()
            op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
            op.available = file_data.vars.dumps()
            op.chosen = self.point_data.list
            op.source = 'OPERATOR'
