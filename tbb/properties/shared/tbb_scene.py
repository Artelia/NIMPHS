# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, StringProperty

from tbb.properties.utils import update_progress_bar


class TBB_Scene(PropertyGroup):
    """Main property of the Toolsbox blender add-on. This data structure holds all Scene data for the add-on."""

    register_cls = True
    is_custom_base_cls = False

    #: dict: Dictionary of file data used for both modules.
    #        Shape is ```{"uid": file_data, "uid": file_data, ...}```
    file_data: dict = {"ops": None}

    #: bpy.props.BoolProperty: State of the 'create sequence' operation (used by all 'create sequence' operators)
    create_sequence_is_running: BoolProperty(
        name="Create sequence state",
        description="State of the 'create sequence' operation (used by all 'create sequence' operators)",
        default=False,
    )

    #: bpy.props.FloatProperty: Progress bar value which is used by the progress bar when modal operators are running
    progress_value: FloatProperty(
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
    progress_label: StringProperty(
        name="Progress label",
        default="Progress",  # noqa: F821
        update=update_progress_bar,
    )
