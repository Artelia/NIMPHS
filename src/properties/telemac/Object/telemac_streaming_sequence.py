# <pep8 compliant>
from bpy.props import BoolProperty

from ...shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_TelemacStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """
    'Streaming sequence' settings for the TELEMAC module.
    """

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )
