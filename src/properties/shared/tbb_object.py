# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty

from .tbb_object_settings import TBB_ObjectSettings


class TBB_Object(PropertyGroup):
    """
    Main property of the Toolsbox blender add-on for objects. This data structure holds all Object data for the add-on.
    """

    #: TBB_ObjectSettings: Holds object settings for both OpenFOAM and TELEMAC modules
    settings: PointerProperty(type=TBB_ObjectSettings)

    #: bpy.props.BoolProperty: Describe if this object is a sequence which updates when the frame changes.
    is_streaming_sequence: BoolProperty(
        name="Is on frame change sequence",
        description="Describe if this object is a sequence which updates when the frame changes",
        default=False,
    )
