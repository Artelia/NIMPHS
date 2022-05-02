# <pep8 compliant>
from bpy.props import PointerProperty

from ..clip import TBB_OpenfoamClipProperty
from ...shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_OpenfoamStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """
    'Streaming sequence' settings for the OpenFOAM module.
    """

    #: TBB_OpenfoamClipProperty: Clip settings of the sequence.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)
