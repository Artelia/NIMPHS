# <pep8 compliant>
from bpy.types import Context

import numpy as np
from pyvista import OpenFOAMReader, UnstructuredGrid


# Dynamically load enum items for the scalars property
def clip_scalar_items(_self, context: Context) -> list:
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


def clip_scalar_items_sequence(self, _context: Context) -> list:
    items = []

    # If the saved list is empty, recreate it
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


def encode_value_ranges(mesh: UnstructuredGrid) -> str:
    output = ""

    for value in mesh.point_data.keys():
        array = mesh.get_array(name=value, preference="points")

        # 'Normal' value (1D)
        if len(array.shape) == 1:
            min = np.min(array)
            max = np.max(array)
            output += value + "@" + "value" + "/" + "{:.4f}".format(min) + "/" + "{:.4f}".format(max)

        # 'Vector' value (2D)
        if len(array.shape) == 2:
            dim = array.shape[1]
            minima = [np.min(array[:, i]) for i in range(dim)]
            maxima = [np.max(array[:, i]) for i in range(dim)]
            output += value + "@vector_value_" + str(dim)
            for i in range(dim):
                output += "/" + "{:.4f}".format(minima[i]) + "/" + "{:.4f}".format(maxima[i])

        output += ";"

    return output


def get_value_range_from_name(value_ranges: str, name: str, value_type: str) -> dict | None:
    values = value_ranges.split(";")

    for value in values:
        if name in value:
            content = value.split("/")[1:]

            # 'Normal' value
            if value_type == "value":
                return {"min": float(content[0]), "max": float(content[1])}

            if value_type == "vector_value":
                dim = int(value.split("/")[0][-1])
                min, max = [], []
                for i in range(dim):
                    min.append(float(content[i]))
                    max.append(float(content[i + dim]))
                return {"min": min, "max": max}

    return None


def set_clip_values(self, value: float) -> None:
    if self.name is not None:
        value_type = self.name.split("@")[1]
        range = get_value_range_from_name(self.value_ranges, self.name, value_type)

        # 'Normal' value
        if value_type == "value":
            if value < range["min"]:
                self["value"] = range["min"]
            elif value > range["max"]:
                self["value"] = range["max"]
            else:
                self["value"] = value

        # 'Vector' value
        if value_type == "vector_value":
            pass


def get_clip_values(self):
    if self.name is not None:
        value_type = self.name.split("@")[1]
        return self[value_type]

    print("ERROR::get_clip_values: unknown value type '" + str(self.name) + "'")
    return None
