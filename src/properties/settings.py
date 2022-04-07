from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty

class TBB_settings(PropertyGroup):
    file_path: StringProperty(
        name="OpenFoam file",
        description="Path to the .foam file"
    )

    preview_time_step: IntProperty(
        name="Preview time step",
        description="Time step used for the preview section",
        min=0,
        soft_min=0,
        max=25,
        soft_max=25,
        step=1,
        default=5
    )

    start_time: IntProperty(
        name="Start time step",
        description="Starting point of the sequence",
        min=0,
        soft_min=0,
        max=25,
        soft_max=25,
        step=1,
        default=0
    )

    end_time: IntProperty(
        name="End time step",
        description="Ending point of the sequence",
        min=0,
        soft_min=0,
        max=25,
        soft_max=25,
        step=1,
        default=0
    )

    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=True
    )