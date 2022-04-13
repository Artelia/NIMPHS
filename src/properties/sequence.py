from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    FloatVectorProperty,
    FloatProperty
)

from .utils import scalar_items_sequence

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

    name: StringProperty(
        name="Name",
        description="Name of the sequence",
        default="TBB_sequence"
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

    clip_type: EnumProperty(
        items=[
            ("no_clip", "None", "Do not clip"),
            ("scalar", "Scalars", "Clip a dataset by a scalar"),
            # ("box", "Box", "Clip a dataset by a bounding box defined by the bounds")
        ],
        name="Type",
        description="Choose the clipping method",
        default="no_clip",
    )

    clip_scalars: EnumProperty(
        items=scalar_items_sequence,
        name="Scalars",
        description="Name of scalars to clip on"
    )

    clip_scalars_list: StringProperty(
        name="Clip scalars list",
        description="Save the list of available scalars",
        default=""
    )

    clip_invert: BoolProperty(
        name="Invert",
        description="Flag on whether to flip/invert the clip. When True, only the mesh below value will be kept. \
When False, only values above value will be kept",
        default=False
    )

    clip_value: FloatProperty(
        name="Value",
        description="Set the clipping value",
        default=0.5
    )

    clip_vector_value: FloatVectorProperty(
        name="Value",
        description="Set the clipping value",
        default=(0.5, 0.5, 0.5)
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