# <pep8 compliant>
from nimphs.properties.shared.module_streaming_sequence_settings import NIMPHS_ModuleStreamingSequenceSettings


class NIMPHS_TelemacStreamingSequenceProperty(NIMPHS_ModuleStreamingSequenceSettings):
    """'streaming sequence' settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False
