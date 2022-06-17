# <pep8 compliant>
from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_TelemacStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """'Streaming sequence' settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False
