# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, StringProperty, PointerProperty

from ..clip import TBB_OpenFOAMClipProperty
from ..utils import set_sequence_anim_length, get_sequence_anim_length


class TBB_OpenFOAMSequenceProperty(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Name of the sequence",
        default="Openfoam_sequence",
    )

    file_path: StringProperty(
        name="File path",
        description="File to read when updating the sequence",
        default="",
    )

    is_streaming_sequence: BoolProperty(
        name="Is on frame change sequence",
        description="Describes if this object is a sequence which updates when the frame changes",
        default=False,
    )

    update: BoolProperty(
        name="Update on frame change",
        description="Update this sequence whenever the frame changes",
        default=False,
    )

    frame_start: IntProperty(
        name="Frame start",
        description="Starting frame for the 'on frame change' sequence type",
        default=-1,
    )

    anim_length: IntProperty(
        name="Animation length",
        description="Length of the animation",
        default=0,
        set=set_sequence_anim_length,
        get=get_sequence_anim_length,
    )

    max_length: IntProperty(
        name="Maximum sequence length",
        description="Maximum length of the sequence (available time steps)",
        default=1,
    )

    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    list_point_data: StringProperty(
        name="Point data list",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default="",
    )

    clip: PointerProperty(type=TBB_OpenFOAMClipProperty)
