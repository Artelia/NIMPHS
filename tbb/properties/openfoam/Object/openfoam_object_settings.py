# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty

from tbb.properties.openfoam.Object.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty


class TBB_OpenfoamObjectSettings(PropertyGroup):
    """
    Data structure which holds object related settings for the OpenFOAM module.
    """
    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamStreamingSequenceProperty: OpenFOAM streaming sequence properties
    streaming_sequence: PointerProperty(type=TBB_OpenfoamStreamingSequenceProperty)
