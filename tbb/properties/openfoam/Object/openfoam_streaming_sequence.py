# <pep8 compliant>
from bpy.props import PointerProperty

from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings
from tbb.properties.openfoam.openfoam_clip import TBB_OpenfoamClipProperty
from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_OpenfoamStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """'Streaming sequence' settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamImportSettings: Import settings.
    import_settings: PointerProperty(type=TBB_OpenfoamImportSettings)

    #: TBB_OpenfoamClipProperty: Clip settings of the sequence.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)
