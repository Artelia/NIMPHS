# <pep8 compliant>
from bpy.types import Operator, Context, Object
from bpy.props import PointerProperty, IntProperty, StringProperty, EnumProperty

from tbb.panels.utils import draw_point_data, get_selected_object
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class TBB_CreateSequence(Operator):
    """Base class of the 'CreateSequence' operators."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.props.EnumProperty: Indicate which module to use. Enum in ['OpenFOAM', 'TELEMAC'].
    module: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicate whether the operator should run modal or not. Enum in ['OpenFOAM', 'TELEMAC']",
        items=[
            ('OpenFOAM', "OpenFOAM", "Use OpenFOAM module"),  # noqa: F821
            ('TELEMAC', "TELEMAC", "Use TELEMAC module"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    def update_start(self, _context: Context) -> None:  # noqa D417
        """
        Make sure the user can't select a wrong value.

        Args:
            _context (Context): context
        """

        if self.start > self.max_length - 1:
            self.start = self.max_length - 1
        elif self.start < 0:
            self.start = 0

    #: bpy.props.IntProperty: Starting point of the sequence.
    start: IntProperty(
        name="Start",  # noqa F821
        description="Starting point of the sequence",
        default=0,
        update=update_start
    )

    #: bpy.props.IntProperty: Maximum length of the sequence.
    max_length: IntProperty(
        name="Max length",  # noqa F821
        description="Maximum length of the sequence",
        default=1,
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.props.StringProperty: Name to give to the generated sequence object.
    name: StringProperty(
        name="Name",  # noqa F821
        description="Name to give to the generated sequence object",
        default="Mesh",  # noqa F821
    )

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: bpy.types.Object: Selected object
    obj: Object = None

    @classmethod
    def poll(self, context: Context) -> bool:
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

            row = box.row()
            op = row.operator("tbb.add_point_data", text="Add", icon='ADD')
            op.available = file_data.vars.dumps()
            op.chosen = self.point_data.list
            op.source = 'OPERATOR'
