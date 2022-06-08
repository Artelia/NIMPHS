# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, IntProperty


class TBB_TelemacInterpolateProperty(PropertyGroup):
    """TELEMAC interpolation properties."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.types.EnumProperty: Type of the interpolation, enum in ['NONE', 'LINEAR']
    type: EnumProperty(
        name="Type",  # noqa: F821
        description="Type of the interpolation",
        items=[
            ("NONE", "None", "None"),  # noqa: F821
            ("LINEAR", "Linear", "Apply a linear interpolation"),  # noqa: F821
        ]
    )

    #: bpy.types.IntProperty: Number of time steps to add between two time points
    time_steps: IntProperty(
        name="Time steps",
        description="Number of time steps to add between two time points",
        default=1,
        min=1,
        soft_min=1,
        soft_max=50,
    )
