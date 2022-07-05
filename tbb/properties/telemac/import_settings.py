# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class TBB_TelemacImportSettings(PropertyGroup):
    """Import settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False