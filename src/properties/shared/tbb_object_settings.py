# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from ..openfoam.Object.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty
from ..telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty


class TBB_ObjectSettings(PropertyGroup):
    """
    Data structure which holds 'streaming sequence' settings for all the modules.
    """

    #: TBB_OpenfoamStreamingSequenceProperty: OpenFOAM streaming sequence properties
    openfoam: PointerProperty(type=TBB_OpenfoamStreamingSequenceProperty)

    #: TBB_TelemacStreamingSequenceProperty: TELEMAC streaming sequence properties
    telemac: PointerProperty(type=TBB_TelemacStreamingSequenceProperty)
