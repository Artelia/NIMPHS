# <pep8 compliant>
from bpy.props import FloatProperty, FloatVectorProperty


import numpy as np
from typing import Union
import logging

from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)


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
