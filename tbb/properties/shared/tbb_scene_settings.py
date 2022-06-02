# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from tbb.properties.telemac.Scene.telemac_settings import TBB_TelemacSettings
from tbb.properties.openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings


class TBB_SceneSettings(PropertyGroup):
    """
    Data structure which holds scene settings for all the modules.
    """
    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamSettings: OpenFOAM scene settings
    openfoam: PointerProperty(type=TBB_OpenfoamSettings)

    #: TBB_TelemacSettings: TELEMAC scene settings
    telemac: PointerProperty(type=TBB_TelemacSettings)
