# <pep8 compliant>
from bpy.types import Operator, Context, Object
from bpy.props import PointerProperty, IntProperty, StringProperty, EnumProperty

from tbb.operators.shared.utils import update_start
from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class TBB_CreateSequence(Operator):
    """Base class of 'CreateSequence' operators."""

    register_cls = False
    is_custom_base_cls = True

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: int: Number of maximum point data that the use can import
    limit_add_point_data: int = 24

    #: bpy.types.Object: Selected object
    obj: Object = None

    # -------------------------------- #
    # /!\ For testing purpose only /!\ #
    # -------------------------------- #
    #: bpy.props.StringProperty: Use this property to pass data as a JSON stringified block of data.
    test_data: StringProperty(
        name="Test data",
        description="Use this property to pass data as a JSON stringified block of data",
        default=""
    )

    #: bpy.props.EnumProperty: Indicate which mode to use for this operator. Enum in ['MODAL', 'TEST'].
    mode: EnumProperty(
        name="Mode",                                    # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['MODAL', 'TEST']",
        items=[
            ('MODAL', "Modal", "Run modal"),            # noqa: F821
            ('TEST', "Test", "Run for unit tests"),     # noqa: F821
        ],
        options={'HIDDEN'},                             # noqa: F821
    )

    #: bpy.props.EnumProperty: Indicate which module to use. Enum in ['OpenFOAM', 'TELEMAC'].
    module: EnumProperty(
        name="Mode",                                            # noqa: F821
        description="Indicate which module to use. Enum in ['OpenFOAM', 'TELEMAC']",
        items=[
            ('OpenFOAM', "OpenFOAM", "Use OpenFOAM module"),    # noqa: F821
            ('TELEMAC', "TELEMAC", "Use TELEMAC module"),       # noqa: F821
        ],
        options={'HIDDEN'},                                     # noqa: F821
    )

    #: bpy.props.IntProperty: Starting frame / time point of the sequence.
    start: IntProperty(
        name="Start",  # noqa F821
        description="Starting frame / time point of the sequence",
        default=0,
        update=update_start,
        soft_min=0,
        min=0
    )

    #: bpy.props.IntProperty: Maximum length / time point of the sequence.
    max: IntProperty(
        name="Max",             # noqa F821
        description="Maximum length / time point of the sequence",
        default=1,
        options={'HIDDEN'},     # noqa F821
    )

    #: bpy.props.StringProperty: Name to give to the generated sequence object.
    name: StringProperty(
        name="Name",        # noqa F821
        description="Name to give to the generated sequence object",
        default="NAME",     # noqa F821
    )

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None:
            return False

        return obj.tbb.module in ['OpenFOAM', 'TELEMAC'] and not context.scene.tbb.m_op_running

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

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

            # Update list of chosen point data from this operator. Ugly but it works.
            self.point_data.list = context.scene.tbb.op_vars.dumps()
            draw_point_data(box, self.point_data, show_range=False, edit=True, src='OPERATOR')

            if context.scene.tbb.op_vars.length() < self.limit_add_point_data:
                row = box.row()
                op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
                op.available = file_data.vars.dumps()
                op.chosen = self.point_data.list
                op.source = 'OPERATOR'
