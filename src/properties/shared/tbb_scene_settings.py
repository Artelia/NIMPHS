# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from ..openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings
from ..telemac.Scene.telemac_settings import TBB_TelemacSettings


class TBB_SceneSettings(PropertyGroup):
    """
    Data structure which holds scene settings for all the modules.
    """

    #: TBB_OpenfoamSettings: OpenFOAM scene settings
    openfoam: PointerProperty(type=TBB_OpenfoamSettings)

    #: TBB_TelemacSettings: TELEMAC scene settings
    telemac: PointerProperty(type=TBB_TelemacSettings)
