# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, BoolProperty

from tbb.properties.telemac.telemac_interpolate import TBB_TelemacInterpolateProperty
from tbb.properties.telemac.Object.telemac_mesh_sequence import TBB_TelemacMeshSequenceProperty
from tbb.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty


class TBB_TelemacObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.StringProperty: Name of the variable used for the 'z-values' of the vertices.
    z_name: StringProperty(
        name="Name of z-value",
        description="Name of the variable used for the 'z-values' of the vertices",
        default=""
    )

    #: bpy.props.BoolProperty: Indicate whether this mesh sequence is from a 3D simulation or not.
    is_3d_simulation: BoolProperty(
        name="Is 3D simulation",
        description="Indicate whether this mesh sequence is from a 3D simulation or not",
        default=False
    )

    #: bpy.props.TBB_TelemacInterpolateProperty: Interpolation settings
    interpolate: PointerProperty(type=TBB_TelemacInterpolateProperty)

    #: TBB_TelemacStreamingSequenceProperty: TELEMAC 'streaming sequence' properties.
    s_sequence: PointerProperty(type=TBB_TelemacStreamingSequenceProperty)

    #: TBB_TelemacMeshSequenceProperty: TELEMAC 'mesh sequence' properties.
    m_sequence: PointerProperty(type=TBB_TelemacMeshSequenceProperty)
