# <pep8 compliant>
from bpy.types import Operator, Context, Object
from bpy.props import EnumProperty, PointerProperty

import time

from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.properties.utils import VariablesInformation


class TBB_CreateSequence(Operator):
    """Base class of the 'CreateSequence' operators."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.props.EnumProperty: Indicates whether the operator should run modal or not. Enum in ['MODAL', 'NORMAL']
    mode: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicates whether the operator should run modal or not. Enum in ['MODAL', 'NORMAL']",
        items=[
            ('MODAL', "Modal", "TODO"),  # noqa: F821
            ('NORMAL', "Normal", "TODO"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: str: JSON strigified list of point data to import as vertex colors.
    list: str = VariablesInformation().dumps()

    #: bpy.types.Object: Selected object
    obj: Object = None

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

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

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        layout = self.layout
        tmp_data = context.scene.tbb.tmp_data["ops"]

        # Import point data
        box = layout.box()
        row = box.row()
        row.prop(self.point_data, "import_data", text="Import point data")

        if self.point_data.import_data:

            self.point_data.list = self.list
            draw_point_data(box, self.point_data, show_range=False, edit=True, source='OPERATOR')

            row = box.row()
            op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
            op.available = tmp_data.vars_info.dumps()
            op.chosen = self.point_data.list
            op.source = 'OPERATOR'

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Stop the 'create sequence' process.

        Common stop function for OpenFOAM and TELEMAC 'create sequence' operators.

        Args:
            context (Context): context
            cancelled (bool, optional): ask to report 'create sequence cancelled'. Defaults to False.
        """

        # Reset timer if it was running modal
        if self.timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)
            self.timer = None

        context.scene.tbb.create_sequence_is_running = False
        context.scene.tbb.progress_value = -1.0

        if cancelled:
            self.report({'INFO'}, "Create sequence cancelled")
