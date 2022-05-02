# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, StringProperty

from ..utils import set_sequence_anim_length, get_sequence_anim_length


class TBB_ModuleStreamingSequenceSettings(PropertyGroup):
    """
    'Streaming sequence' properties.
    This data structure holds common data used in the OpenFOAM and TELEMAC modules.
    """

    #: bpy.props.StringProperty: Name of the sequence.
    name: StringProperty(
        name="Name",
        description="Name of the sequence",
        default="",
    )

    #: bpy.props.BoolProperty: Update this sequence whenever the frame changes.
    update: BoolProperty(
        name="Update on frame change",
        description="Update this sequence whenever the frame changes",
        default=False,
    )

    #: bpy.props.StringProperty: File to read when updating the sequence.
    file_path: StringProperty(
        name="File path",
        description="File to read when updating the sequence",
        default="",
    )

    #: bpy.props.IntProperty: Starting frame of the sequence.
    frame_start: IntProperty(
        name="Frame start",
        description="Starting frame of the sequence",
        default=-1,
    )

    #: bpy.props.IntProperty: Length of the animation.
    anim_length: IntProperty(
        name="Animation length",
        description="Length of the animation",
        default=0,
        set=set_sequence_anim_length,
        get=get_sequence_anim_length,
    )

    #: bpy.props.IntProperty: Maximum length of the sequence (available time steps).
    max_length: IntProperty(
        name="Maximum sequence length",
        description="Maximum length of the sequence (available time steps)",
        default=1,
    )

    #: bpy.props.BoolProperty: Import point data as vertex color groups.
    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    #: bpy.props.StringProperty: List of point data to import as vertex color groups. Separate each with a semicolon.
    list_point_data: StringProperty(
        name="Point data list",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default="",
    )
