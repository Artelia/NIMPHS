from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, PointerProperty
from rna_prop_ui import rna_idprop_ui_create

# Dynamically load enum items for the scalars property
def scalar_items(self, context):
    items = []
    if context.scene.tbb_temp_data.mesh_data != None:
        for key in context.scene.tbb_temp_data.mesh_data.point_data.keys():
            items.append((key, key, "Undocumented"))
    return items

def update_scalar_value_prop(self, context):
    scalars_props = context.scene.tbb_clip.scalars_props
    scalars = scalars_props.scalars
    if scalars_props.get("value") == None:
        rna_idprop_ui_create(
            scalars_props,
            "value",
            default=0.5,
            min=0.0,
            soft_min=0.0,
            max=1.0,
            soft_max=1.0,
            description="Set the clipping value"
        )

    prop = scalars_props.id_properties_ui("value")
    default = scalars_props["value"]

    values = context.scene.tbb_temp_data.mesh_data[scalars]
    # TODO: not working with vector values
    print(values)
    new_max = max(values)
    new_min = min(values)
    if new_max < default or new_min > default: default = new_min
    prop.update(default=default, min=new_min, soft_min=new_min, max=new_max, soft_max=new_max)

class TBB_clip_scalar(PropertyGroup):
    scalars: EnumProperty(
        items=scalar_items,
        name="Scalars",
        description="Name of scalars to clip on",
        update=update_scalar_value_prop
    )

    # value: FloatProperty Dynamically created

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