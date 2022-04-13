import numpy as np
from pyvista import OpenFOAMReader

# Dynamically load enum items for the scalars property
def scalar_items(self, context):
    temp_data = context.scene.tbb_temp_data
    items = []
    if temp_data.mesh_data != None:
        for key in temp_data.mesh_data.point_data.keys():
            value_type = len(temp_data.mesh_data.get_array(name=key, preference="point").shape)
            # Vector value
            if value_type == 2:
                items.append((key + "@vector_value", key, "Undocumented"))
            # Normal value
            elif value_type == 1:
                items.append((key + "@value", key, "Undocumented"))
    return items



def scalar_items_sequence(self, context):
    items = []

    # If the saved list in empty, recreate it
    if self.clip_scalars_list == "":
        file_reader = OpenFOAMReader(self.file_path)
        file_reader.set_active_time_point(0)
        data = file_reader.read()
        mesh = data["internalMesh"]

        point_data_list = ""
        for key in mesh.point_data.keys():
            value_type = len(mesh.get_array(name=key, preference="point").shape)
            # Vector value
            if value_type == 2:
                point_data_list += key + "@vector_value" + ";"
            # Normal value
            elif value_type == 1:
                point_data_list += key + "@value" + ";"

        self.clip_scalars_list = point_data_list

    # Read from the saved list
    for scalar in self.clip_scalars_list.split(";"):
        if scalar != "":
            name = scalar.split("@")[0]
            items.append((scalar, name, "Undocumented"))

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
        new_max = [np.max(values[:, 0]), np.max(values[:, 1]), np.max(values[:, 2])]
        new_min = [np.min(values[:, 0]), np.min(values[:, 1]), np.min(values[:, 2])]
        if new_max < default.to_list() or new_min > default.to_list(): default = np.min(new_min)
        prop.update(default=default, min=np.min(new_min), soft_min=np.min(new_min), max=np.min(new_max), soft_max=np.min(new_max))