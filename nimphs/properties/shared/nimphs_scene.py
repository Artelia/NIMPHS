# <pep8 compliant>
from bpy.types import PropertyGroup, Object, Context
from bpy.props import BoolProperty, FloatProperty, StringProperty, PointerProperty

from nimphs.properties.utils.point_data import PointDataManager


def update_progress_bar(_self, context: Context) -> None:
    """
    Update function for the custom progress bar. Tag all info areas for redraw.

    Args:
        context (Context): context
    """

    areas = context.window.screen.areas
    for area in areas:
        if area.type == 'INFO':
            area.tag_redraw()


class NIMPHS_Scene(PropertyGroup):
    """Data structure which holds all Scene data for the add-on."""

    register_cls = True
    is_custom_base_cls = False

    # A variable where we can store the original draw function of VIEW_3D_HT_tool_header
    def view_3d_ht_tool_header_draw(s, c):  # noqa: D102
        return None

    #: bool: Indicate if the draw method of VIEW_3D_HT_tool_header has already been saved.
    view_3d_ht_tool_header_draw_saved: bool = False

    #: dict: Dictionary of file data used for all modules and all objects.
    #        Shape is: ```{"ops": file_data for current operator, "uid": obj file_data, "uid": obj file_data, ...}```
    file_data: dict = {"ops": None}

    #: PointDataManager: Place to store temporary point data information for operators.
    op_vars: PointDataManager = PointDataManager()

    #: bpy.props.PointerPropery: Target object on which extract point data.
    op_target: PointerProperty(type=Object)

    #: bpy.props.BoolProperty: Indicate if a modal operator is running.
    m_op_running: BoolProperty(
        name="Modal operator running",
        description="Indicate if a modal operator is running.",
        default=False,
    )

    #: bpy.props.FloatProperty: Value used by the progress bar when modal operators are running
    m_op_value: FloatProperty(
        name="Progress value",
        default=-1.0,
        min=-1.0,
        soft_min=0.0,
        max=101.0,
        soft_max=100.0,
        precision=1,
        subtype="PERCENTAGE",  # noqa: F821
        update=update_progress_bar,
    )

    #: bpy.props.StringProperty: Label displayed on the progress bar
    m_op_label: StringProperty(
        name="Progress label",
        default="Progress",  # noqa: F821
        update=update_progress_bar,
    )
