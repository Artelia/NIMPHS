# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, IntProperty


class TBB_TelemacInterpolateProperty(PropertyGroup):
    """
    TELEMAC interpolation properties.
    """
    register_cls = True
    is_custom_base_cls = False

    #: bpy.types.EnumProperty: Type of the interpolation
    type: EnumProperty(
        name="Type",
        description="Type of the interpolation",
        items=[
            ("none", "None", "None"),
            ("linear", "Linear", "Apply a linear interpolation"),
        ]
    )

    #: bpy.types.IntProperty: Number of time steps to add between two time points
    time_steps: IntProperty(
        name="Time steps",
        description="Number of time steps to add between two time points",
        default=0,
        min=0,
        soft_min=0,
    )