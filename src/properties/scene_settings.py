# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty


scene_settings_dynamic_props = [
    ("preview_time_point", "Time step used for the preview section"),
    ("start_time_point", "Starting point of the sequence"),
    ("end_time_point", "Ending point of the sequence"),
    ("anim_length", "Length of the animation"),
]


class TBB_SceneSettings(PropertyGroup):
    """
    Main panel settings. Contains 4 'dynamic' properties:

    | **preview_time_point**: *bpy.types.IntProperty*, time step used for the preview section
    | **start_time_point**: *bpy.types.IntProperty*, starting point of the sequence
    | **end_time_point**: *bpy.types.IntProperty*, ending point of the sequence
    | **anim_length**: *bpy.types.IntProperty*, length of the animation
    """

    # preview_time_point: IntProperty dynamically created

    # start_time_point: IntProperty dynamically created

    # end_time_point: IntProperty dynamically created

    # anim_length: IntProperty dynamically created

    #: bpy.types.IntProperty: Starting point of the sequence
    frame_start: IntProperty(
        name="Frame start",
        description="Starting point of the sequence",
        default=1
    )

    #: bpy.types.StringProperty: Path to the file
    file_path: StringProperty(
        name="File path",
        description="Path to the imported file",
    )

    #: bpy.types.BoolProperty: Import point data as vertex color groups
    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    #: bpy.types.StringProperty: List of point data to import as vertex color groups. Separate each with a semicolon
    list_point_data: StringProperty(
        name="Point data list",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default="",
    )

    #: bpy.types.StringProperty: Name of the sequence object
    sequence_name: StringProperty(
        name="Sequence name",
        description="Name of the sequence object",
        default="",
    )
