# <pep8 compliant>
import numpy as np
from pyvista import OpenFOAMReader


# Dynamically load enum items for the scalars property
def clip_scalar_items(_self, context) -> list:
    tmp_data = context.scene.tbb_openfoam_tmp_data
    items = []

    if tmp_data.mesh is not None:
        for key in tmp_data.mesh.point_data.keys():
            value_type = len(tmp_data.mesh.get_array(name=key, preference="point").shape)
            # Vector value
            if value_type == 2:
                items.append((key + "@vector_value", key, "Undocumented"))
            # 'Normal' value
            elif value_type == 1:
                items.append((key + "@value", key, "Undocumented"))
    return items


def clip_scalar_items_sequence(self, _context) -> list:
    items = []

    # If the saved list in empty, recreate it
    if self.clip.scalar.list == "":
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

        self.clip.scalar.list = point_data_list

    # Read from the saved list
    for scalar in self.clip.scalar.list.split(";"):
        if scalar != "":
            name = scalar.split("@")[0]
            items.append((scalar, name, "Undocumented"))

    return items
