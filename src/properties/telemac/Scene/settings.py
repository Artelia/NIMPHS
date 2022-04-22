# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty

from ..utils import update_var_names


settings_dynamic_properties = [
    ("preview_time_point", "Time step used for the preview section"),
    ("start_time_point", "Starting point of the sequence"),
    ("end_time_point", "Ending point of the sequence"),
]


class TBB_TelemacSettings(PropertyGroup):
    """
    Main panel settings. Contains 4 'dynamic' properties:

    | **preview_time_point**: *bpy.types.IntProperty*, time step used for the preview section
    | **start_time_point**: *bpy.types.IntProperty*, starting point of the sequence
    | **end_time_point**: *bpy.types.IntProperty*, ending point of the sequence
    """

    # preview_time_point: IntProperty dynamically created

    # start_time_point: IntProperty dynamically created

    # end_time_point: IntProperty dynamically created

    #: bpy.types.StringProperty: Path to the .foam file
    file_path: StringProperty(
        name="TELEMAC file path",
        description="Path to the .slf file",
    )

    #: bpy.types.BoolProperty: State of the 'create sequence' operator
    create_sequence_is_running: BoolProperty(
        name="Create sequence is running",
        description="State of the 'create sequence' operator",
        default=False,
    )

    #: bpy.types.EnumProperty: Name of point data to preview
    preview_point_data: EnumProperty(
        items=update_var_names,
        name="Point data",
        description="Name of point data to preview",
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
        default="OpenFOAM",
    )
