# <pep8 compliant>
from bpy.props import BoolProperty

from ...shared.streaming_sequence_property import TBB_StreamingSequenceProperty


class TBB_TelemacStreamingSequenceProperty(TBB_StreamingSequenceProperty):
    """
    'Streaming sequence' settings for the TELEMAC module.
    """

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )
