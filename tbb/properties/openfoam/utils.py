# <pep8 compliant>
import json
from bpy.types import Context
from bpy.props import FloatProperty, FloatVectorProperty


import numpy as np
from typing import Union
import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.operators.utils import get_temporary_data


def available_point_data(_self, context: Context) -> list:
    """
    Generate the list of available point data.

    Args:
        context (Context): context

    Returns:
        list: available point data
    """

    obj = get_selected_object(context)
    if obj is None:
        return [("None", "None", "None")]

    tmp_data = get_temporary_data(obj)
    if tmp_data is None or not tmp_data.is_ok():
        return [("None", "None", "None")]

    items = []
    vars = tmp_data.vars_info
    for name, range, type, dim in zip(vars["names"], vars["ranges"], vars["types"], vars["dimensions"]):
        identifier = {"names": [name], "ranges": [range], "types": [type], "dimensions": [dim]}
        items.append((json.dumps(identifier, ), name, "Undocumented"))

    return items


def update_preview_time_point(self, context: Context) -> None:
    """
    Update selected value of preview time point (make sure you can only select available time points).

    Args:
        context (Context): context
    """

    obj = get_selected_object(context)
    if obj is None:
        log.error("No selected object. Defaults to 0.", exc_info=1)
        self.preview_time_point = 0

    tmp_data = get_temporary_data(obj)
    if tmp_data is None or not tmp_data.is_ok():
        log.error("No temporary data available. Defaults to 0.", exc_info=1)
        self.preview_time_point = 0

    if self.preview_time_point > tmp_data.nb_time_points:
        self.preview_time_point = tmp_data.nb_time_points
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
        data = json.loads(self.name)
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

            for i in range(data["dimension"]):
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
        value_type = json.loads(self.name)["type"]

        if value_type == 'SCALAR':
            return self.get("value", 0.5)

        if value_type == 'VECTOR':
            return [val for val in self.get("vector_value", (0.5, 0.5, 0.5))]

    log.error(f"Unknown value type {self.name}, return np.inf", exc_info=1)
    return np.inf
