# <pep8 compliant>
import json
from bpy.types import Context
from bpy.props import FloatProperty, FloatVectorProperty


import numpy as np
from typing import Union
import logging

from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)


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
    if self.bl_rna.name == 'TBB_OpenfoamObjectSettings':
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


def set_clip_values(self: Union[FloatProperty, FloatVectorProperty], value: float) -> None:
    """
    Set clip values.

    Function triggered when the user sets a new clip value. This let us to make sure the new value
    is in the value range of the selected scalar. Set the value to the nearest bound if outside the range.

    Args:
        self (Union[FloatProperty, FloatVectorProperty]): property
        value (float): new value
    """

    if self.name is not None:
        data = VariablesInformation(self.name).get(0)
        ranges = data["range"]["local"]

        if data["type"] == 'SCALAR':
            if value < ranges["min"]:
                self["value"] = ranges["min"]
            elif value > ranges["max"]:
                self["value"] = ranges["max"]
            else:
                self["value"] = value

        if data["type"] == 'VECTOR':
            # This is ugly, but it works. In fact, self["value"] and
            # self["vector_value"] do not exist until they are manipulated (get/set).
            self["vector_value"] = (0.5, 0.5, 0.5)

            for i in range(data["dim"]):
                if value[i] < ranges["min"][i]:
                    self["vector_value"][i] = ranges["min"][i]
                elif value[i] > ranges["max"][i]:
                    self["vector_value"][i] = ranges["max"][i]
                else:
                    self["vector_value"][i] = value[i]


def get_clip_values(self) -> Union[float, list]:
    """
    Get clip values.

    Function triggered when the UI fetches a clip value. Defaults to np.inf.

    Returns:
        Union[float, list]: value
    """

    if self.name is not None:
        value_type = VariablesInformation(self.name).get(0, prop='TYPE')

        if value_type == 'SCALAR':
            return self.get("value", 0.5)

        if value_type == 'VECTOR':
            return [val for val in self.get("vector_value", (0.5, 0.5, 0.5))]

    log.error(f"Unknown value type {self.name}, return np.inf", exc_info=1)
    return np.inf
