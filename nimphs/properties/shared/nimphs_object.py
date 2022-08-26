# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty, StringProperty

from nimphs.properties.shared.nimphs_object_settings import NIMPHS_ObjectSettings


class NIMPHS_Object(PropertyGroup):
    """Main property of the add-on for objects. This holds all Object data for the add-on."""

    register_cls = True
    is_custom_base_cls = False

    #: NIMPHS_ObjectSettings: Holds object settings for all modules.
    settings: PointerProperty(type=NIMPHS_ObjectSettings)

    #: bpy.props.StringProperty: Module name
    module: StringProperty(
        name="Module name",
        description="Module name. Enum in ['OpenFOAM', 'TELEMAC']",
        default="None",
    )

    #: bpy.props.StringProperty: Unique identifier for each object of the add-on to access file_data.
    uid: StringProperty(
        name="UID",  # noqa: F821
        description="Unique identifier",
        default="None",
    )

    #: bpy.props.BoolProperty: Indicate if this object is a sequence which updates when the frame changes.
    is_streaming_sequence: BoolProperty(
        name="Is a streaming sequence",
        description="Indicate if this object is a sequence which updates when the frame changes",
        default=False,
    )

    #: bpy.props.BoolProperty: Indicate whether this object is a mesh sequence or not.
    is_mesh_sequence: BoolProperty(
        name="Is a mesh sequence",
        description="Indicate whether this object is a mesh sequence or not",
        default=False
    )
