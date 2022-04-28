# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty, IntProperty

from ..utils import update_var_names


telemac_settings_dynamic_props = [
    ("preview_time_point", "Time step used for the preview section"),
    ("start_time_point", "Starting point of the sequence"),
    ("end_time_point", "Ending point of the sequence"),
    ("anim_length", "Length of the animation"),
]


class TBB_TelemacSettings(PropertyGroup):
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

    #: bpy.types.StringProperty: Path to the .foam file
    file_path: StringProperty(
        name="TELEMAC file path",
        description="Path to the .slf file",
    )

    #: bpy.types.FloatVectorProperty: Hold original dimensions of the mesh
    preview_obj_dimensions: FloatVectorProperty(
        name="Preview object dimensions",
        description="Dimensions of the preview object",
        default=(1.0, 1.0, 1.0),
    )

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize_preview_obj: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize_sequence_obj: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
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
        default="TELEMAC",
    )

    #: bpy.types.EnumProperty: Select a sequence type
    sequence_type: EnumProperty(
        items=[
            ("mesh_sequence",
             "Mesh sequence",
             "Make a sequence by adding shape keys for each time step (good option for small meshes)"),
            ("streaming_sequence",
             "Streaming sequence",
             "TODO (good option for large meshes)"),
        ],
        name="Sequence type",
        description="Select a sequence type",
    )
