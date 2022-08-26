# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty

from nimphs.properties.telemac.interpolate import NIMPHS_TelemacInterpolateProperty
from nimphs.properties.telemac.telemac_mesh_sequence import NIMPHS_TelemacMeshSequenceProperty
from nimphs.properties.telemac.telemac_streaming_sequence import NIMPHS_TelemacStreamingSequenceProperty


class NIMPHS_TelemacObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.StringProperty: Name of the variable used for the 'z-values' of the vertices.
    z_name: StringProperty(
        name="Name of z-value",
        description="Name of the variable used for the 'z-values' of the vertices",
        default=""
    )

    #: bpy.props.NIMPHS_TelemacInterpolateProperty: Interpolation settings.
    interpolate: PointerProperty(type=NIMPHS_TelemacInterpolateProperty)

    #: NIMPHS_TelemacStreamingSequenceProperty: TELEMAC 'streaming sequence' properties.
    s_sequence: PointerProperty(type=NIMPHS_TelemacStreamingSequenceProperty)

    #: NIMPHS_TelemacMeshSequenceProperty: TELEMAC 'mesh sequence' properties.
    m_sequence: PointerProperty(type=NIMPHS_TelemacMeshSequenceProperty)
