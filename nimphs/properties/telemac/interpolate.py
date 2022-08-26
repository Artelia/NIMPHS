# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, IntProperty


class NIMPHS_TelemacInterpolateProperty(PropertyGroup):
    """Interpolation settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.EnumProperty: Type of the interpolation. Enum in ['NONE', 'LINEAR']
    type: EnumProperty(
        name="Type",                                                # noqa: F821
        description="Type of the interpolation",
        items=[
            ("NONE", "None", "None"),                               # noqa: F821
            ("LINEAR", "Linear", "Apply a linear interpolation"),   # noqa: F821
        ]
    )

    #: bpy.props.IntProperty: Number of data to generate between two known data points
    steps: IntProperty(
        name="Steps",  # noqa: F821
        description="Number of data to generate between two known data points",
        default=1,
        min=1,
        soft_min=1,
        soft_max=5,
    )
