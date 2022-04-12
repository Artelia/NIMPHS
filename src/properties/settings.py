from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .utils import scalar_items

class TBB_settings(PropertyGroup):
    file_path: StringProperty(
        name="OpenFoam file",
        description="Path to the .foam file"
    )

    create_sequence_is_running: BoolProperty(
        name="Create sequence is running",
        default=False
    )

    # preview_time_step: IntProperty dynamically created

    # start_time: IntProperty dynamically created

    # end_time: IntProperty dynamically created

    preview_point_data: EnumProperty(
        items=scalar_items,
        name="Point data",
        description="Name of point data to preview"
    )

    sequence_name: StringProperty(
        name="Sequence name",
        description="Name of the sequence object",
        default="TBB"
    )

    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False
    )

    list_point_data: StringProperty(
        name="Point data list",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default=""
    )

settings_dynamic_properties = [
    ("preview_time_step", "Time step used for the preview section"),
    ("start_time", "Starting point of the sequence"),
    ("end_time", "Ending point of the sequence")
]