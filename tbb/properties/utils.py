# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Context, VIEW3D_HT_tool_header, Object, Mesh

import logging
log = logging.getLogger(__name__)

import json
import numpy as np
from typing import Union, Any

DEV_MODE = False


class VariablesInformation():
    """Data structure to manage point data information for both modules."""

    #: list: Variable names
    names: list = []
    #: list: Variable units
    units: list = []
    #: list: Variable types
    types: list = []
    #: list: Value ranges {"local" {"min" xx, "max" xx}, "global" {"min" xx, "max" xx}}
    ranges: list = []
    #: list: Variable dimensions
    dimensions: list = []

    def __init__(self, json_string: str = "") -> None:
        """
        Init method of the class.

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
            Union[dict, Any, None]: information on variables.
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
                return output

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
                return None

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

        output = "Variables information:\n"
        output += "NAMES: " + str(self.names) + '\n'
        output += "UNITS: " + str(self.units) + '\n'
        output += "RANGES: " + str(self.ranges) + '\n'
        output += "TYPES: " + str(self.types) + '\n'
        output += "DIMENSIONS: " + str(self.dimensions) + '\n'
        return output


class InterpInfo():
    """Base class of utility classes to get interpolation information for sequence objects."""

    #: bool: Indicate if data has been successfully computed
    has_data: bool = False
    #: bool: Indicate the current time point is an existing time point
    exists: bool = True
    #: int: Frame at the "left" of the current time point
    left_frame: int = 0
    #: int: Number of time steps between each existing time point
    time_steps: int = 0
    #: int: Current frame
    frame: int = 0
    #: int: Next existing time point
    right: int = 0
    #: int: Previous existing time point
    left: int = 0

    def __init__(self) -> None:
        """Init method of the class."""

        self.has_data = False
        self.exists = True
        self.left_frame = 0
        self.time_steps = 0
        self.frame = 0
        self.right = 0
        self.left = 0

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        output = "Interpolation information:\n"
        output += "EXISTS: " + ("True\n" if self.exists else "False\n")
        output += "LEFT FRAME: " + str(self.left_frame) + "\n"
        output += "TIME STEPS: " + str(self.time_steps) + "\n"
        output += "FRAME: " + str(self.frame) + "\n"
        output += "RIGHT: " + str(self.right) + "\n"
        output += "LEFT: " + str(self.left) + "\n"
        return output


class InterpInfoStreamingSequence(InterpInfo):
    """Utility class to get interpolation information for 'Streaming Sequence' objects."""

    def __init__(self, frame: int, start: int, time_steps: int) -> None:
        """
        Init method of the class.

        Args:
            frame (int): current frame
            start (int): start frame of the sequence
            time_steps (int): number of time steps between each time point
        """

        self.compute(frame, start, time_steps)

    def compute(self, frame: int, start: int, time_steps: int) -> None:
        """
        Compute time information for interpolation of 'Streaming Sequence' objects.

        Args:
            frame (int): _description_
            start (int): _description_
            time_steps (int): _description_
        """

        time_point = frame - start
        self.has_data = True

        if time_steps == 0:
            # If it is an existing time
            self.exists = True
            self.left_frame = frame
            self.time_steps = 0
            self.frame = frame
            self.right = time_point
            self.left = time_point
        else:
            # If it is an interpolated time point
            info = self.scan(time_point, time_steps)

            self.exists = info[2]
            self.left_frame = start + (time_steps + 1) * info[0]
            self.time_steps = time_steps
            self.frame = frame
            self.right = info[1]
            self.left = info[0]

    def scan(self, time_point: int, time_steps: int) -> tuple[int, int, bool]:
        """
        Scan time information for interpolation of 'Streaming Sequence' objects.

        Args:
            time_point (int): current time point
            time_steps (int): number of time steps between each time point

        Returns:
            tuple[int, int, bool]: left time point, right time point, if left time point is an existing time point
        """

        modulo = time_point % (time_steps + 1)
        l_time_point = int((time_point - modulo) / (time_steps + 1))
        r_time_point = l_time_point + 1

        return l_time_point, r_time_point, modulo == 0


class InterpInfoMeshSequence(InterpInfo):
    """Utility class to get interpolation information for 'Mesh Sequence' objects."""

    def __init__(self, obj: Object, frame: int, threshold: float = 0.0001) -> None:
        """
        Init method of the class.

        Args:
            obj (Object): 'Mesh Sequence' object
            frame (int): current frame
            threshold (float, optional): shape_key value threshold. Defaults to 0.0001.
        """

        self.compute(obj, frame, threshold=threshold)

    def compute(self, obj: Object, frame: int, threshold: float = 0.0001) -> None:
        """
        Compute time information for interpolation of 'Mesh Sequence' objects.

        Args:
            obj (Object): sequence object
            frame (int): current frame
            threshold (float, optional): shape_key value threshold. Defaults to 0.0001.
        """

        # Get information from shape keys
        info = self.scan(obj.data, threshold=threshold)

        if info["frame_start"] <= frame <= info["frame_end"]:
            self.has_data = True

            if info["state"] == 'BASIS':
                self.exists = True
                self.left_frame = info["frame_start"]
                self.time_steps = 0
                self.frame = frame
                self.right = info["start_offset"] + 1
                self.left = info["start_offset"]

            elif info["state"] == 'EXISTING':
                self.exists = True
                self.left_frame = info["frames"][0]
                self.time_steps = 0
                self.frame = frame
                self.right = info["time_points"][0] + 1
                self.left = info["time_points"][0]

            elif info["state"] == 'INTERPOLATED':
                self.exists = False
                self.left_frame = info["frames"][0]
                self.time_steps = np.abs(info["frames"][0] - info["frames"][1]) - 1
                self.frame = frame
                self.right = info["time_points"][1]
                self.left = info["time_points"][0]

        else:
            self.has_data = False

    def scan(self, bmesh: Mesh, threshold: float = 0.0001) -> None:
        """
        Scan time information for interpolation of 'Mesh Sequence' objects.

        .. code-block:: text

            Example of output:

            * Mesh sequence: frame start = 12, anim length = 50.
            * Shape keys are linearly interpolated (2 time steps between each time point)
            * Current frame: 125

                Timeline
                Frames:     (12)⌄    (15)⌄                  (125)⌄                       (159)⌄
                                *  +  +  *  ...   *  +  +  *  +  +  *  +  +  *  ...  *  +  +  *
                Time points: (0)⌃     (1)⌃    (36)⌃    (37)⌃    (38)⌃    (39)⌃            (49)⌃

            Outputs:
            {
                "state": enum in ['BASIS', 'EXISTING', 'INTERPOLATED'] here 'INTERPOLATED',
                "start_offset": 0,
                "time_points": [37, 38],
                "ids": [123, 126],
                "frame_start": 12,
                "frame_end": 159
            }

        Args:
            bmesh (Mesh): mesh from which to get the information
            threshold (float, optional): threshold on the shape_key value. Defaults to 0.0001.
        """

        fcurves = bmesh.shape_keys.animation_data.action.fcurves
        start_offset = int(bmesh.shape_keys.key_blocks[1].name) - 1
        output = {
            "state": "",
            "start_offset": start_offset,
            "time_points": [],
            "frames": [],
            "frame_start": fcurves[0].keyframe_points[0].co[0],
            "frame_end": fcurves[-1].keyframe_points[-1].co[0]
        }

        # Get active shape_keys information
        # Note: range starts from 1 because there is one more shape_key ('Basis')
        for fcurve, key_id in zip(fcurves, range(1, len(fcurves) + 1, 1)):
            if bmesh.shape_keys.key_blocks[key_id].value > threshold:
                output["frames"].append(fcurve.keyframe_points[1].co[0])
                output["time_points"].append(key_id + start_offset)

        # Check more precise info on time points
        if len(output["time_points"]) == 0:
            # If there are no active shape_keys
            output["state"] = 'BASIS'

        elif len(output["time_points"]) == 1:
            if bmesh.shape_keys.key_blocks[output["time_points"][0] - start_offset].value != 1.0:
                # If the time point is not an existing time point (value is not 1.0 for the shape_key)

                if output["time_points"][0] == 1:
                    # Check if this shape_key is between time points 0 and 1
                    # First time point
                    output["state"] = 'INTERPOLATED'
                    output["time_points"].append(start_offset)
                    output["frames"].append(fcurves[0].keyframe_points[0].co[0])
                else:
                    # Last time point
                    output["state"] = 'INTERPOLATED'
                    output["time_points"].append(len(fcurves))
                    output["frames"].append(fcurves[-1].keyframe_points[-1].co[0])
            else:
                # This shape_key is on an existing time point
                output["state"] = 'EXISTING'

        elif len(output["time_points"]) == 2:
            # This shape_key represents an interpolated time point
            output["state"] = 'INTERPOLATED'

        # Make sure it is always sorted
        output["frames"].sort()
        output["time_points"].sort()

        return output


def set_sequence_length(self, value: int) -> None:
    """
    Set length of the animation.

    Function triggered when the user sets a new animation length. This let us to make sure the new value
    is not higher than the available time steps.

    Args:
        self (IntProperty): property
        value (int): new value
    """

    if value > self.max:
        self["length"] = self.max
    elif value < 0:
        self["length"] = 0
    else:
        self["length"] = value


def get_sequence_length(self) -> int:
    """
    Return the animation length value.

    Returns:
        int: value
    """

    return self.get("length", 0)


def available_point_data(self, context: Context) -> list:
    """
    Generate the list of available point data.

    Args:
        context (Context): context

    Returns:
        list: available point data
    """

    try:
        file_data = context.scene.tbb.file_data[self.id_data.tbb.uid]  # Works for objects
    except AttributeError:  # Raised when called from an operator (WindowManager object has no attribute 'tbb')
        file_data = context.scene.tbb.file_data["ops"]

    if file_data is None or not file_data.is_ok() or file_data.vars.length() == 0:
        return [("NONE", "None", "None")]

    # Add a 'None' field for preview_point_data
    if self.bl_rna.name == 'TBB_ObjectSettings':
        items = [(json.dumps({"name": "None"}), "None", "Do not import")]
    else:
        items = []

    for id in range(file_data.vars.length()):
        identifier = file_data.vars.get(id)
        items.append((json.dumps(identifier), identifier["name"], "Undocumented"))

    return items


def update_preview_time_point(self, context: Context) -> None:  # noqa D417
    """
    Update selected value of time point (make sure the user can only select available time points).

    Args:
        context (Context): context
    """

    try:
        file_data = context.scene.tbb.file_data[self.id_data.tbb.uid]
    except KeyError:
        return [("NONE", "None", "None")]

    if not file_data.is_ok():
        return [("NONE", "None", "None")]

    if self.preview_time_point >= file_data.nb_time_points:
        self.preview_time_point = file_data.nb_time_points - 1
    elif self.preview_time_point < 0:
        self.preview_time_point = 0


@persistent
def tbb_on_save_pre(_dummy) -> None:
    """
    Save data before the blender file is saved.

    Args:
        scene (Scene): scene
    """

    for obj in bpy.data.objects:
        file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
        if file_data is not None:
            obj.tbb.settings.point_data.save = file_data.vars.dumps()


def update_progress_bar(_self, context: Context) -> None:
    """
    Update function for the custom progress bar. Tag all info areas for redraw.

    Args:
        context (Context): context
    """

    areas = context.window.screen.areas
    for area in areas:
        if area.type == 'INFO':
            area.tag_redraw()


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
        m_op_value = context.scene.tbb.m_op_value
        if m_op_value >= 0.0 and m_op_value <= 100.0:
            self.layout.separator()
            text = context.scene.tbb.m_op_label
            self.layout.prop(context.scene.tbb, "m_op_value", text=text, slider=True)

    # Replace the draw function by our new function
    # Blender crashes sometimes when using the progress bar in dev mode
    if not DEV_MODE:
        VIEW3D_HT_tool_header.draw = new_draw


# A variable where we can store the original draw function
def info_header_draw(s, c) -> None:  # noqa: D103
    return None
