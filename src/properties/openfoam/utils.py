# <pep8 compliant>
from bpy.types import Context

import numpy as np
from pyvista import UnstructuredGrid


def encode_scalar_names(mesh: UnstructuredGrid) -> str:
    """
    Encode scalar names for the *list* attribute of TBB_OpenfoamClipProperty.

    :param mesh: mesh data read from the OpenFOAM file
    :type mesh: UnstructuredGrid
    :rtype: str
    """

    output = ""

    for value in mesh.point_data.keys():
        array = mesh.get_array(name=value, preference="point")

        # 'Normal' value (1D)
        if len(array.shape) == 1:
            output += value + "@" + "value"

        # 'Vector' value (2D)
        if len(array.shape) == 2:
            output += value + "@vector_value"

        output += ";"

    return output


def update_scalar_names(self, _context: Context) -> list:
    """
    Update the list of scalar names for EnumProperties.

    :type _context: Context
    :rtype: list
    """

    items = []
    try:
        # Raises an AttributeError when this call comes from TBB_OpenfoamSettings.preview_point_data
        scalar_list = self.clip.scalar.list
        items.append(("None@None", "None", "None"))
    except AttributeError:
        scalar_list = self.list

    # Read from the saved list
    for scalar in scalar_list.split(";"):
        if scalar != "":
            name = scalar.split("@")[0]
            items.append((scalar, name, "Undocumented"))

    return items


def encode_value_ranges(mesh: UnstructuredGrid) -> str:
    """
    Encode values ranges for the *value_ranges* attribute of TBB_OpenfoamClipProperty.

    :param mesh: mesh data read from the OpenFOAM file
    :type mesh: UnstructuredGrid
    :rtype: str
    """

    output = ""

    for value in mesh.point_data.keys():
        array = mesh.get_array(name=value, preference="point")

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
    """
    Return the value range corresponding to the given scalar name.

    .. code-block:: text

        Return a dict with the following members:
        "min": contains min values
        "max": contains max values

    :param value_ranges: encoded value ranges
    :type value_ranges: str
    :param name: name of the scalar to retrieve
    :type name: str
    :param value_type: type of the scalar ("value" or "vector_value_dim")
    :type value_type: str
    :rtype: dict | None
    """

    values = value_ranges.split(";")

    for value in values:
        if name in value:
            content = value.split("/")[1:]

            if value_type == "value":
                return {"min": float(content[0]), "max": float(content[1])}

            if value_type == "vector_value":
                dim = int(value.split("/")[0][-1])
                min, max = [], []
                for i in range(dim):
                    min.append(float(content[i * 2]))
                    max.append(float(content[i * 2 + 1]))
                return {"min": min, "max": max}

    return None


def set_clip_values(self, value: float) -> None:
    """
    Function triggered when the user sets a new clip value. This let us to make sure the new value
    is in the value range of the selected scalar. Set the value to the nearest bound if outside the range.

    :param value: new value
    :type value: float
    """

    if self.name is not None:
        value_type = self.name.split("@")[1]
        ranges = get_value_range_from_name(self.value_ranges, self.name, value_type)

        if value_type == "value":
            if value < ranges["min"]:
                self[value_type] = ranges["min"]
            elif value > ranges["max"]:
                self[value_type] = ranges["max"]
            else:
                self[value_type] = value

        if value_type == "vector_value":
            # This is ugly, but it works. In fact, self["value"] and
            # self["vector_value"] do not exist until they are manipulated (get/set).
            self[value_type] = (0.5, 0.5, 0.5)

            dim = len(ranges["min"])
            for i in range(dim):
                if value[i] < ranges["min"][i]:
                    self[value_type][i] = ranges["min"][i]
                elif value[i] > ranges["max"][i]:
                    self[value_type][i] = ranges["max"][i]
                else:
                    self[value_type][i] = value[i]


def get_clip_values(self) -> float | list | None:
    """
    Function triggered when the UI fetches a clip value.

    :return: value
    :rtype: float | list | None
    """

    if self.name is not None:
        value_type = self.name.split("@")[1]

        if value_type == "value":
            return self.get(value_type, 0.5)  # returns a default value (0.5) if it has no been set

        if value_type == "vector_value":
            return [val for val in self.get(value_type, (0.5, 0.5, 0.5))]

    print("ERROR::get_clip_values: unknown value type '" + str(self.name) + "'")
    return None
