# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty

from .tbb_scene_settings import TBB_SceneSettings


class TBB_Scene(PropertyGroup):
    """
    Main property of the Toolsbox blender add-on. This data structure holds all Scene data for the add-on.
    """

    #: TBB_Settings: Holds scene settings for both OpenFOAM and TELEMAC modules
    settings: PointerProperty(type=TBB_SceneSettings)

    #: BoolProperty: State of the 'create sequence' operation (used by all 'create sequence' operators)
    create_sequence_is_running: BoolProperty(
        name="Create sequence state",
        description="State of the 'create sequence' operation (used by all 'create sequence' operators)",
        default=False,
    )
