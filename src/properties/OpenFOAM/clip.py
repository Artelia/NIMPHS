# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, PointerProperty, FloatProperty, FloatVectorProperty, StringProperty

from .utils import clip_scalar_items, set_clip_values, get_clip_values


class TBB_OpenFOAMClipScalarProperty(PropertyGroup):
    value: FloatProperty(
        name="Value",
        description="Set the clipping value",
        default=0.5,
        precision=6,
        step=1,
        set=set_clip_values,
        get=get_clip_values,
    )

    vector_value: FloatVectorProperty(
        name="Value",
        description="Set the clipping value",
        default=(0.5, 0.5, 0.5),
        precision=6,
        step=1,
        set=set_clip_values,
        get=get_clip_values,
    )

    value_ranges: StringProperty(
        name="Value ranges",
        description="Save the value ranges of each scalar",
        default="",
    )

    name: EnumProperty(
        items=clip_scalar_items,
        name="Scalars",
        description="Name of scalars to clip on",
    )

    list: StringProperty(
        name="Clip scalars list",
        description="Save the list of available scalars",
        default="",
    )

    invert: BoolProperty(
        name="Invert",
        description="Flag on whether to flip/invert the clip. When True, only the mesh below 'value' will be kept. When False, only values above 'value' will be kept",
        default=False,
    )


class TBB_OpenFOAMClipProperty(PropertyGroup):
    type: EnumProperty(
        items=[
            ("no_clip", "None", "Do not clip"),
            ("scalar", "Scalars", "Clip a dataset by a scalar"),
            # ("box", "Box", "Clip a dataset by a bounding box defined by the bounds"),
        ],
        name="Type",
        description="Choose the clipping method",
        default="no_clip",
    )

    scalar: PointerProperty(type=TBB_OpenFOAMClipScalarProperty)
