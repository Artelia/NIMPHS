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

    #: bpy.props.StringProperty: List of files to accept when importing OpenFOAM files.
    openfoam_extensions: StringProperty(
        name="OpenFOAM extensions",
        description="List of files to accept when importing OpenFOAM files",
        default="*.foam",
    )

    #: bpy.props.StringProperty: List of files to accept when importing TELEMAC files.
    telemac_extensions: StringProperty(
        name="TELEMAC extensions",
        description="List of files to accept when importing TELEMAC files",
        default="*.slf",
    )
