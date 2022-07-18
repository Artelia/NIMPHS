# <pep8 compliant>
from bpy.types import Context

import logging
log = logging.getLogger(__name__)

import json

from tbb.properties.utils.point_data import PointDataManager


def update_clip_value(self, value: float) -> None:  # noqa: D417
    """
    Set clip value.

    Function triggered when the user sets a new clip value. This let us to make sure the new value
    is in the value range of the selected scalar. Set the value to the nearest bound if outside the range.

    Args:
        value (float): new value
    """

    if self.name is not None:
        data = PointDataManager(self.name).get(0)

        if value < data.range.minL:
            self["value"] = data.range.minL

        elif value > data.range.maxL:
            self["value"] = data.range.maxL

        else:
            self["value"] = value


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
        items.append((identifier.dumps(), identifier.name, "Undocumented"))

    return items


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
