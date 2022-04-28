# <pep8 compliant>
from bpy.props import PointerProperty

from ...sequence_settings import TBB_StreamingSequenceProperty
from ..clip import TBB_OpenfoamClipProperty


class TBB_OpenfoamSequenceProperty(TBB_StreamingSequenceProperty):
    """
    'Streaming sequence' settings for the OpenFOAM module.
    """

    #: TBB_OpenfoamClipProperty: Clip settings of the sequence.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)
