# <pep8 compliant>
from bpy.props import BoolProperty

from ...streaming_sequence_property import TBB_StreamingSequenceProperty


class TBB_TelemacSequenceProperty(TBB_StreamingSequenceProperty):
    """
    'Streaming sequence' settings for the TELEMAC module.
    """

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )
