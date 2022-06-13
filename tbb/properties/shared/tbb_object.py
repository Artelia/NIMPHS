# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty, StringProperty

from tbb.properties.shared.tbb_object_settings import TBB_ObjectSettings


class TBB_Object(PropertyGroup):
    """Main property of the Toolsbox blender addon for objects. This holds all Object data for the addon."""

    register_cls = True
    is_custom_base_cls = False

    #: dict: Dictionary of temporary data used for both modules.
    #        Shape is ```{"uid": tmp_data, "uid": tmp_data, ...}```
    tmp_data: dict = {}

    #: TBB_ObjectSettings: Holds object settings for both OpenFOAM and TELEMAC modules.
    settings: PointerProperty(type=TBB_ObjectSettings)

    #: bpy.props.StringProperty: Module name
    module: StringProperty(
        name="Module name",
        description="Module name, enum in ['None', 'OpenFOAM', 'TELEMAC']",
        default="None",
    )

    #: bpy.props.BoolProperty: Describe if this object is a sequence which updates when the frame changes.
    is_streaming_sequence: BoolProperty(
        name="Is on frame change sequence",
        description="Describe if this object is a sequence which updates when the frame changes",
        default=False,
    )

    #: bpy.props.BoolProperty: Indicate whether this object is part of a mesh sequence or not
    is_mesh_sequence: BoolProperty(
        name="Is part of a mesh sequence",
        description="Indicate whether this object is part of a mesh sequence or not",
        default=False
    )

    #: bpy.props.StringProperty: Unique identifier for each 'tbb object'.
    uid: StringProperty(
        name="UID",  # noqa: F821
        description="Unique identifier",
        default="None",
    )
