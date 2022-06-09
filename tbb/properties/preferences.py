# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty


class TBB_Preferences(PropertyGroup):
    """Addon preferences properties."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.EnumProperty: Define the log level, enum in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].
    log_level: EnumProperty(
        name="Log level",
        description="Define the log level, enum in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
        items=[
            ('DEBUG', 'Debug', 'Debug level'),
            ('INFO', 'Info', 'Info level'),
            ('WARNING', 'Warning', 'Warning level'),
            ('ERROR', 'Error', 'Error level'),
            ('CRITICAL', 'Critical', 'Critical level'),
        ],
    )
