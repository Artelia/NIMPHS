# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, StringProperty

import os
from pathlib import Path


class NIMPHS_InstallerProperties(PropertyGroup):
    """Add-on installer properties."""

    register_cls = False
    is_custom_base_cls = False

    #: bpy.props.EnumProperty: Installation configuration. Enum in ['CLASSIC', 'ADVANCED'].
    configuration: EnumProperty(
        name="Configuration",                                       # noqa: F821
        description="Installation configuration. Enum in ['CLASSIC', 'ADVANCED']",
        items=[
            ('CLASSIC', 'Classic', 'Install all the necessary dependendices needed to make this add-on work. \
This configuration does not include under-development features'),   # noqa: F821
            ('ADVANCED', 'Advanced', 'Install all the necessary dependendices needed to make this add-on work \
plus other python packages for under-development features. This configuration might not work if you did not \
follow the instructions in the developers manual'),                # noqa: F821
        ],
    )

    #: bpy.props.BoolProperty: Indicate if we have to insert '--force-reinstall' when instatlling dependencies.
    reinstall: BoolProperty(
        name="Re-install",  # noqa: F821
        description="Force re-installation of all the python packages (equivalent to --force-reinstall)",
        default=False,
    )

    requirements: StringProperty(
        name="Python requirements",
        description="Requirements.txt file path",
        default=os.path.join(os.path.abspath(Path(__file__).parent.parent), "requirements.txt")
    )
