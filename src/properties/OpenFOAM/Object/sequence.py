# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    FloatVectorProperty,
    FloatProperty
)

from ..utils import clip_scalar_items_sequence


class TBB_OpenFOAMSequenceProperty(PropertyGroup):
    is_on_frame_change_sequence: BoolProperty(
        name="Is on frame change sequence",
        description="Describes if this object is a sequence which updates when the frame changes",
        default=False
    )

    update_on_frame_change: BoolProperty(
        name="Update on frame change",
        description="Update this sequence whenever the frame changes",
        default=False
    )

    name: StringProperty(
        name="Name",
        description="Name of the sequence",
        default="Openfoam_sequence"
    )

    frame_start: IntProperty(
        name="Frame start",
        description="Starting frame for the 'on frame change' sequence type",
        default=-1
    )

    anim_length: IntProperty(
        name="Animation length",
        description="Length of the animation",
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
        items=clip_scalar_items_sequence,
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
        description="Flag on whether to flip/invert the clip. When True, only the mesh below value will be kept. When False, only values above value will be kept",
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
