# <pep8 compliant>
from bpy.types import Context, VIEW3D_HT_tool_header

import logging
log = logging.getLogger(__name__)
from typing import Union, Any
import json

DEV_MODE = True


class VariablesInformation():
    """Data structure to manage point data information for both modules."""

    def __init__(self, json_string: str = "") -> None:
        """
        Init method of the class. Can fill in information given JSON stringified data.

        Args:
            json_string (str, optional): JSON stringified data. Defaults to "".
        """

        self.names = []
        self.units = []
        self.types = []
        self.ranges = []
        self.dimensions = []

        if json_string != "":
            data = json.loads(json_string)
            if data.get("names", None) is not None:
                self.names = data.get("names", [])
                self.units = data.get("units", [""] * len(self.names))
                self.types = data.get("types", [])
                self.ranges = data.get("ranges", [])
                self.dimensions = data.get("dimensions", [])
            elif data.get("name", None) is not None:
                self.append(data=data)

    def get(self, id: Union[str, int], prop: str = "") -> Union[dict, Any, None]:
        """
        Return information about the variable at the given index.

        Args:
            id (Union[str, int]): index can be an int or the name of a variable.
            prop (str, optional): name of a specific property to get. If not set return all. Defaults to "".

        Returns:
            Union[dict, Any, None]: dict containing all information. Defaults to None.
        """

        if isinstance(id, str):
            try:
                id = self.names.index(id)
            except ValueError:
                log.critical(f"Unkonw id {id}", exc_info=1)
                return None

        if id < self.length():

            if prop == "":
                output = {
                    "name": self.names[id],
                    "unit": self.units[id],
                    "type": self.types[id],
                    "range": self.ranges[id],
                    "dim": self.dimensions[id],
                }

            elif prop in ['NAME', 'UNIT', 'TYPE', 'RANGE', 'DIM']:
                if prop == 'NAME':
                    return self.names[id]
                if prop == 'UNIT':
                    return self.units[id]
                if prop == 'TYPE':
                    return self.types[id]
                if prop == 'RANGE':
                    return self.ranges[id]
                if prop == 'DIM':
                    return self.dimensions[id]

            else:
                log.critical(f"Property '{prop}' is undefined", exc_info=1)

            return output

        else:
            log.critical(f"Index '{id}' out of bound (length = {len(self.names)})", exc_info=1)
            return None

    def clear(self) -> None:
        """Clear all data."""

        self.names.clear()
        self.units.clear()
        self.types.clear()
        self.ranges.clear()
        self.dimensions.clear()

    def remove(self, id: int) -> None:
        """
        Remove variable at the given index.

        Args:
            id (int): index of the variable to remove
        """

        if id < self.length():
            self.names.pop(id)
            self.units.pop(id)
            self.types.pop(id)
            self.ranges.pop(id)
            self.dimensions.pop(id)
        else:
            log.critical(f"Index '{id}' out of bound (length = {len(self.names)})", exc_info=1)

    def append(self, name: str = 'NONE', unit: str = "", range: dict = None, type: str = 'SCALAR', dim: int = 1,
               data: dict = None) -> None:
        """
        Append new variable information to the data structure.

        Args:
            name (str, optional): name. Defaults to "".
            unit (str, optional): unit. Defaults to "".
            range (dict, optional): value ranges. Defaults to None.
            type (str, optional): type. Defaults to 'SCALAR'.
            dim (int, optional): dimension. Defaults to 1.
            data (dict, optional): data. Defaults to None.
        """

        default_range = {"local": {"min": None, "max": None}, "global": {"min": None, "max": None}}

        if data is not None:
            self.names.append(data.get("name", ""))
            self.units.append(data.get("unit", ""))
            self.types.append(data.get("type", ""))
            self.ranges.append(data.get("range", default_range))
            self.dimensions.append(data.get("dim", ""))

        else:
            self.names.append(name)
            self.units.append(unit)
            if range is None:
                self.ranges.append(default_range)
            else:
                if range.get("local", None) is not None and range.get("global", None) is not None:
                    self.ranges.append(range)
                elif range.get("local", None) is None and range.get("global", None) is not None:
                    self.ranges.append({"local": default_range["local"], "global": range["global"]})
                elif range.get("local", None) is not None and range.get("global", None) is None:
                    self.ranges.append({"local": range["local"], "global": default_range["global"]})
                else:
                    self.ranges.append(default_range)

            self.types.append(type)
            self.dimensions.append(dim)

    def dumps(self) -> str:
        """
        Serialize VariablesInformation to a JSON formatted str.

        Returns:
            str: JSON stringified data
        """

        data = {
            "names": self.names,
            "units": self.units,
            "types": self.types,
            "ranges": self.ranges,
            "dimensions": self.dimensions,
        }

        return json.dumps(data)

    def length(self) -> int:
        """
        Get the number of variables.

        Returns:
            int: number of variables
        """

        return len(self.names)

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        return str(self.names) + " / " + str(self.units) + " / " + str(self.ranges) + " / " + str(self.types) + " / \
" + str(self.dimensions)


def set_sequence_anim_length(self, value: int) -> None:
    """
    Set length of the animation.

    Function triggered when the user sets a new animation length. This let us to make sure the new value
    is not higher than the available time steps.

    Args:
        self (IntProperty): property
        value (int): new value
    """

    if value > self.max_length:
        self["anim_length"] = self.max_length
    elif value < 0:
        self["anim_length"] = 0
    else:
        self["anim_length"] = value


def get_sequence_anim_length(self) -> int:
    """
    Return the animation length value.

    Returns:
        int: value
    """

    return self.get("anim_length", 0)


def update_progress_bar(_self, context: Context):
    """
    Update function for the custom progress bar. Tag all info areas for redraw.

    Args:
        context (Context): context
    """

    areas = context.window.screen.areas
    for area in areas:
        if area.type == 'INFO':
            area.tag_redraw()


def available_point_data(self, context: Context) -> list:
    """
    Generate the list of available point data.

    Args:
        context (Context): context

    Returns:
        list: available point data
    """

    try:
        tmp_data = context.scene.tbb.tmp_data[self.id_data.tbb.uid]  # Works for objects
    except AttributeError:  # Raised when called from an operator (WindowManager object has not attribute 'tbb')
        tmp_data = context.scene.tbb.tmp_data["ops"]

    if tmp_data is None or not tmp_data.is_ok():
        log.error("No file data available")
        return [("NONE", "None", "None")]

    # Add a 'None' field for preview_point_data
    if self.bl_rna.name == 'TBB_ObjectSettings':
        items = [(json.dumps({"name": "None"}), "None", "Do not import")]
    else:
        items = []

    for id in range(tmp_data.vars_info.length()):
        identifier = tmp_data.vars_info.get(id)
        items.append((json.dumps(identifier), identifier["name"], "Undocumented"))

    return items


def update_preview_time_point(self, context: Context) -> None:  # noqa D417
    """
    Update selected value of preview time point (make sure you can only select available time points).

    Args:
        context (Context): context
    """

    try:
        tmp_data = context.scene.tbb.tmp_data[self.id_data.tbb.uid]
    except KeyError:
        log.error("No file data available")
        return [("NONE", "None", "None")]

    if not tmp_data.is_ok():
        return [("NONE", "None", "None")]

    if self.preview_time_point >= tmp_data.nb_time_points:
        self.preview_time_point = tmp_data.nb_time_points - 1
    elif self.preview_time_point < 0:
        self.preview_time_point = 0

# Inspired by: https://blog.michelanders.nl/2017/04/how-to-add-progress-indicator-to-the-info-header-in-blender.html


def register_custom_progress_bar() -> None:
    """Register the custom progress bar."""

    # Save the original draw method of Info header
    global info_header_draw
    info_header_draw = VIEW3D_HT_tool_header.draw

    # Create a new draw function
    def new_draw(self, context):
        global info_header_draw
        # First call to the original function
        info_header_draw(self, context)

        # Then add the prop that acts as a progress bar
        progress_value = context.scene.tbb.progress_value
        if progress_value >= 0.0 and progress_value <= 100.0:
            self.layout.separator()
            text = context.scene.tbb.progress_label
            self.layout.prop(context.scene.tbb, "progress_value", text=text, slider=True)

    # Replace the draw function by our new function
    # Blender crashes sometimes when using the progress bar in dev mode
    if not DEV_MODE:
        VIEW3D_HT_tool_header.draw = new_draw


# A variable where we can store the original draw function
def info_header_draw(s, c):  # noqa: D103
    return None
