from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, BoolProperty

class TBB_settings(PropertyGroup):
    file_path: StringProperty(
        name="OpenFoam file",
        description="Path to the .foam file",
        subtype="FILE_PATH"
    )

    start_time: FloatProperty(
        name="Start time step",
        description="Starting point of the sequence",
        min=0.0,
        soft_min=0.0,
        max=2.0,
        soft_max=2.0,
        step=0.1,
        precision=2,
        default=0.0
    )

    end_time: FloatProperty(
        name="End time step",
        description="Ending point of the sequence",
        min=0.0,
        soft_min=0.0,
        max=2.0,
        soft_max=2.0,
        step=0.1,
        precision=2,
        default=0.0
    )

    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=True
    )