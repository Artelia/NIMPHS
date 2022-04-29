# <pep8 compliant>
from bpy.props import PointerProperty

from ..clip import TBB_OpenfoamClipProperty
from ...shared.streaming_sequence_property import TBB_StreamingSequenceProperty


class TBB_OpenfoamStreamingSequenceProperty(TBB_StreamingSequenceProperty):
    """
    'Streaming sequence' settings for the OpenFOAM module.
    """

    #: TBB_OpenfoamClipProperty: Clip settings of the sequence.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)
