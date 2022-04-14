# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, PointerProperty

from ..utils import clip_scalar_items, update_scalar_value_prop


class TBB_OpenFOAMClipScalarProperty(PropertyGroup):
    # value: FloatProperty Dynamically created

    # vector_value: FloatVectorProperty Dynamically created

    scalars: EnumProperty(
        items=clip_scalar_items,
        name="Scalars",
        description="Name of scalars to clip on",
        update=update_scalar_value_prop
    )

    invert: BoolProperty(
        name="Invert",
        description="Flag on whether to flip/invert the clip. When True, only the mesh below value will be kept. When False, only values above value will be kept",
        default=False
    )


class TBB_OpenFOAMClipProperty(PropertyGroup):
    type: EnumProperty(
        items=[
            ("no_clip", "None", "Do not clip"),
            ("scalar", "Scalars", "Clip a dataset by a scalar"),
            # ("box", "Box", "Clip a dataset by a bounding box defined by the bounds")
        ],
        name="Type",
        description="Choose the clipping method",
        default="no_clip",
    )

    scalars_props: PointerProperty(type=TBB_OpenFOAMClipScalarProperty)
