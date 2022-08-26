# <pep8 compliant>
from nimphs.properties.shared.module_streaming_sequence_settings import NIMPHS_ModuleStreamingSequenceSettings


class NIMPHS_OpenfoamStreamingSequenceProperty(NIMPHS_ModuleStreamingSequenceSettings):
    """'streaming sequence' settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False
