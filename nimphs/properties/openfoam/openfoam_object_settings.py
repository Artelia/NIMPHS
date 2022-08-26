# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from nimphs.properties.openfoam.clip import NIMPHS_OpenfoamClipProperty
from nimphs.properties.openfoam.import_settings import NIMPHS_OpenfoamImportSettings
from nimphs.properties.openfoam.openfoam_streaming_sequence import NIMPHS_OpenfoamStreamingSequenceProperty


class NIMPHS_OpenfoamObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    #: NIMPHS_OpenfoamImportSettings: Import settings.
    import_settings: PointerProperty(type=NIMPHS_OpenfoamImportSettings)

    #: NIMPHS_OpenfoamClipProperty: Clip settings.
    clip: PointerProperty(type=NIMPHS_OpenfoamClipProperty)

    #: NIMPHS_OpenfoamStreamingSequenceProperty: OpenFOAM streaming sequence properties.
    s_sequence: PointerProperty(type=NIMPHS_OpenfoamStreamingSequenceProperty)
