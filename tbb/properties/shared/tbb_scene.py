# <pep8 compliant>
from bpy.types import PropertyGroup, Object
from bpy.props import BoolProperty, FloatProperty, StringProperty, PointerProperty

from tbb.properties.utils import VariablesInformation, update_progress_bar


class TBB_Scene(PropertyGroup):
    """Main property of the add-on. This data structure holds all Scene data for the add-on."""

    register_cls = True
    is_custom_base_cls = False

    #: dict: Dictionary of file data used for all modules and all objects.
    #        Shape is ```{"uid": file_data, "uid": file_data, ...}```
    file_data: dict = {"ops": None}

    #: VariablesInformation: Place to store temporary variables information for operators.
    op_vars: VariablesInformation = VariablesInformation()

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
