# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty

from tbb.properties.utils import set_sequence_anim_length, get_sequence_anim_length


class TBB_ModuleStreamingSequenceSettings(PropertyGroup):
    """
    Module 'streaming sequence' properties.

    This data structure holds common data used in both OpenFOAM and TELEMAC modules.
    """

    register_cls = True
    is_custom_base_cls = True

    #: bpy.props.BoolProperty: Update this sequence whenever the frame changes.
    update: BoolProperty(
        name="Update on frame change",
        description="Update this sequence whenever the frame changes",
        default=False,
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

    #: bpy.props.BoolProperty: Whether to use smooth shading or flat shading
    shade_smooth: BoolProperty(
        name="Shade smooth",
        description="Indicate whether to use smooth shading or flat shading",
        default=False
    )
