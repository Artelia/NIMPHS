# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty


class NIMPHS_InstallerProperties(PropertyGroup):
    """Add-on installer properties."""

    register_cls = False
    is_custom_base_cls = False

    #: bpy.props.EnumProperty: Installation configuration. Enum in ['CLASSIC', 'ADVANCED'].
    configuration: EnumProperty(
        name="Configuration",
        description="Installation configuration. Enum in ['CLASSIC', 'ADVANCED']",
        items=[
            ('CLASSIC', 'Classic', 'Install all the necessary dependcies needed to make this add-on work. \
This configuration does not include under-development features'),   # noqa: F821
            ('ADVANCED', 'Advanced', 'Install all the necessary dependcies needed to make this add-on work \
plus other python packages for under-development features. This configuration might not work if you did not \
follow thse instructions in the developers manual'),                # noqa: F821
        ],
    )

    #: bpy.props.BoolProperty: Indicate if we have to insert '--force-reinstall' when instatlling dependencies.
    reinstall: BoolProperty(
        name="Re-install",
        description="Force re-installation of all the dependencies.",
        default=False,
    )
