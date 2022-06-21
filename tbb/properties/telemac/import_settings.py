# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class TBB_TelemacImportSettings(PropertyGroup):
    """Import settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.BoolProperty: If `True`, compute 'global' value ranges for all the variables.
    compute_value_ranges: BoolProperty(
        name="Compute valuer ranges",  # noqa: F821
        description="If True, compute 'global' value ranges for all the variables.",
        default=False
    )
