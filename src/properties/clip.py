from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, PointerProperty

import numpy as np

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

    values = context.scene.tbb_temp_data.mesh_data[scalars]
    # 1D array
    if len(values.shape) == 1: prop_name = "value"
    # 2D array (array of vectors)
    elif len(values.shape) == 2: prop_name = "vector_value"
    else:
        print("ERROR::update_scalar_value_prop: invalid values shape for data named '" + str(scalars) + "' (shape = " + str(values.shape) + ")")
        return

    try:
        prop = scalars_props.id_properties_ui(prop_name)
    except Exception as error:
        print("ERROR::update_scalar_value_prop: " + str(error))
        return
    
    default = scalars_props[prop_name]
    
    # 1D array
    if len(values.shape) == 1:
        new_max = np.max(values)
        new_min = np.min(values)
        if new_max < default or new_min > default: default = new_min
        prop.update(default=default, min=new_min, soft_min=new_min, max=new_max, soft_max=new_max)

    # 2D array
    elif len(values.shape) == 2:
        new_max = np.max(values)
        new_min = np.min(values)
        if new_max < np.max(default) or new_min > np.min(default): default = (new_min, new_min, new_min)
        prop.update(default=default, min=new_min, soft_min=new_min, max=new_max, soft_max=new_max)


class TBB_clip_scalar(PropertyGroup):
    scalars: EnumProperty(
        items=scalar_items,
        name="Scalars",
        description="Name of scalars to clip on",
        update=update_scalar_value_prop
    )

    # value: FloatProperty Dynamically created

    # vector_value: FloatVectorProperty Dynamically created

    invert: BoolProperty(
        name="Invert",
        description="Flag on whether to flip/invert the clip. When True, only the mesh below value will be kept. \
When False, only values above value will be kept",
        default=False
    )


class TBB_clip(PropertyGroup):
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

    scalars_props: PointerProperty(type=TBB_clip_scalar)