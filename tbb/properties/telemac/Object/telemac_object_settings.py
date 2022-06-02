# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, BoolProperty

from tbb.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from tbb.properties.telemac.Object.telemac_mesh_sequence import TBB_TelemacMeshSequenceProperty


class TBB_TelemacObjectSettings(PropertyGroup):
    """
    Data structure which holds object related settings for the TELEMAC module.
    """
    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.StringProperty: Name of the variable used for the 'z-values' of the vertices
    z_name: StringProperty(
        name="Name of z-value",
        description="Name of the variable used for the 'z-values' of the vertices",
        default=""
    )

    #: bpy.props.BoolProperty: Indicate whether this object is part of a mesh sequence or not
    is_mesh_sequence: BoolProperty(
        name="Is part of a mesh sequence",
        description="Indicate whether this object is part of a mesh sequence or not",
        default=False
    )

    #: TBB_TelemacStreamingSequenceProperty: TELEMAC 'streaming sequence' properties
    streaming_sequence: PointerProperty(type=TBB_TelemacStreamingSequenceProperty)

    #: TBB_TelemacMeshSequenceProperty: TELEMAC 'mesh sequence' properties
    mesh_sequence: PointerProperty(type=TBB_TelemacMeshSequenceProperty)
