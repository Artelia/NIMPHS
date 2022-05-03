# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from .openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty


class TBB_OpenfoamObjectSettings(PropertyGroup):
    """
    Data structure which holds object related settings for the OpenFOAM module.
    """

    #: TBB_OpenfoamStreamingSequenceProperty: OpenFOAM streaming sequence properties
    streaming_sequence: PointerProperty(type=TBB_OpenfoamStreamingSequenceProperty)
