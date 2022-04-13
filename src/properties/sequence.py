from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, StringProperty

class TBB_sequence(PropertyGroup):
    is_tbb_sequence: BoolProperty(
        name="Is a TBB sequence",
        description="Describes if this object is a sequence created with TBB",
        default=False
    )

    update_on_frame_change: BoolProperty(
        name="Update on frame change",
        description="Update this sequence whenever the current frame changes",
        default=False
    )

    frame_start: IntProperty(
        name="Frame start",
        description="Starting frame for the 'on frame change' sequence type",
        default=-1
    )

    frame_end: IntProperty(
        name="Frame end",
        description="Ending frame for the 'on frame change' sequence type",
        default=-1
    )

    file_path: StringProperty(
        name="File path",
        description="File to read when updating the sequence",
        default=""
    )