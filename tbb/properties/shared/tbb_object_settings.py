# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty

from tbb.properties.telemac.Object.telemac_object_settings import TBB_TelemacObjectSettings
from tbb.properties.openfoam.Object.openfoam_object_settings import TBB_OpenfoamObjectSettings


class TBB_ObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for all the modules."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.StringProperty: Module name
    module: StringProperty(
        name="Module name",
        description="Module name, enum in ['None', 'OpenFOAM', 'TELEMAC']",
        default="None",
    )

    #: TBB_OpenfoamObjectSettings: OpenFOAM object properties
    openfoam: PointerProperty(type=TBB_OpenfoamObjectSettings)

    #: TBB_TelemacObjectSettings: TELEMAC object properties
    telemac: PointerProperty(type=TBB_TelemacObjectSettings)
