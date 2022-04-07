from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty, EnumProperty, PointerProperty

# Dynamically load enum items for the scalars property
def items(self, context):
    items = []
    if context.scene.tbb_temp_data.mesh_data != None:
        for key in context.scene.tbb_temp_data.mesh_data.point_data.keys():
            items.append((key, key, "Undocumented"))
    return items

class TBB_clip_scalar(PropertyGroup):
    scalars: EnumProperty(
        items=items,
        name="Scalars",
        description="Name of scalars to clip on"
    )

    value: FloatProperty(
        name="Value",
        description="Set the clipping value",
        min=0.0,
        soft_min=0.0,
        max=1.0,
        soft_max=1.0,
        step=0.001,
        precision=3,
        default=0.5
    )

    invert: BoolProperty(
        name="Invert",
        description="Flag on whether to flip/invert the clip. When True, only the mesh below value will be kept.\
            When False, only values above value will be kept",
        default=False
    )


class TBB_clip(PropertyGroup):
    type: EnumProperty(
        items=[
            ("no_clip", "None", "Do not clip"),
            ("scalar", "Scalars", "Clip a dataset by a scalar"),
            ("box", "Box", "Clip a dataset by a bounding box defined by the bounds")
        ],
        name="Type",
        description="Choose the clipping method",
        default="no_clip",
    )

    scalars_props: PointerProperty(type=TBB_clip_scalar)