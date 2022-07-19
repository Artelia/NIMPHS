# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from tbb.properties.openfoam.clip import TBB_OpenfoamClipProperty
from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings
from tbb.properties.openfoam.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty


class TBB_OpenfoamObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamImportSettings: Import settings.
    import_settings: PointerProperty(type=TBB_OpenfoamImportSettings)

    #: TBB_OpenfoamClipProperty: Clip settings.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)

    #: TBB_OpenfoamStreamingSequenceProperty: OpenFOAM streaming sequence properties.
    s_sequence: PointerProperty(type=TBB_OpenfoamStreamingSequenceProperty)
