# <pep8 compliant>
import logging
log = logging.getLogger(__name__)

import json
import numpy as np
from typing import Union
from copy import deepcopy


class ValueRange():
    """Data structure which hold information on point data value ranges."""

    #: float: local minimum
    minL: float = np.nan
    #: float: global minimum
    minG: float = np.nan
    #: float: local maximum
    maxL: float = np.nan
    #: float: global maximum
    maxG: float = np.nan

    def __init__(self, json_string: str = "") -> None:
        """
        Init method of the class.

        Args:
            json_string (str, optional): JSON stringified data. Defaults to "".
        """

        self.minL = np.nan
        self.minG = np.nan
        self.maxL = np.nan
        self.maxG = np.nan

        # Read data from given json string
        if json_string:

            data = json.loads(json_string)
            self.minL = data.get("minL", np.nan)
            self.minG = data.get("minG", np.nan)
            self.maxL = data.get("maxL", np.nan)
            self.maxG = data.get("maxG", np.nan)

    def dumps(self) -> str:
        """
        Serialize this data structure to a JSON formatted str.

        Returns:
            str: JSON stringified data
        """

        data = {
            "minL": self.minL,
            "minG": self.minG,
            "maxL": self.maxL,
            "maxG": self.maxG
        }

        return json.dumps(data)

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        return "{" + f"minL: {self.minL}, minG: {self.minG}, maxL: {self.maxL}, maxG: {self.maxG}" + "}"


class PointDataInformation():
    """Data structure which hold information on a given point data."""

    #: str: Name of point data
    name: str = ''
    #: str: Unit of point data
    unit: str = ''
    #: ValueRange: Point data value ranges information
    range: ValueRange = ValueRange()

    def __init__(self, name: str, unit: str, range: ValueRange) -> None:
        """
        Init method of the class.

        Args:
            name (str): name
            unit (str): unit
            range (ValueRange): point data value ranges information
        """

        self.name = name
        self.unit = unit
        self.range = range

    def dumps(self) -> str:
        """
        Serialize this data structure to a JSON formatted str.

        Returns:
            str: JSON stringified data
        """

        data = {
            "name": self.name,
            "unit": self.unit,
            "range": self.range.dumps(),
        }

        return json.dumps(data)

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        return "{" + f"name: {self.name}, unit: {self.unit}, range: {self.range}" + "}"


class PointDataManager():
    """Data structure to manage point data information for both modules."""

    #: list[str]: Point data names
    names: list[str] = []
    #: list[str]: Point data units
    units: list[str] = []
    #: list[ValueRange]: List of ValueRange
    ranges: list[ValueRange] = []

    def __init__(self, json_string: str = "") -> None:
        """
        Init method of the class.

        Args:
            json_string (str, optional): JSON stringified data. Defaults to "".
        """

        self.names = []
        self.units = []
        self.ranges = []

        # Read data from given json string
        if json_string:

            data = json.loads(json_string)

            if data.get("names", None) is not None:

                self.names = data.get("names", [])
                self.units = data.get("units", [""] * len(self.names))
                if data.get("ranges", None) is not None:
                    # Read point data value ranges
                    for value_range_str in data["ranges"]:
                        self.ranges.append(ValueRange(value_range_str))
                else:
                    self.ranges = []

            elif data.get("name", None) is not None:

                self.append(data=data)

    def length(self) -> int:
        """
        Get the number of point data.

        Returns:
            int: number of point data
        """

        return len(self.names)

    def clear(self) -> None:
        """Clear all data."""

        self.names.clear()
        self.units.clear()
        self.ranges.clear()

    def remove(self, id: int) -> None:
        """
        Remove point data at the given index.

        Args:
            id (int): index of point data to remove
        """

        if id < self.length():
            self.names.pop(id)
            self.units.pop(id)
            self.ranges.pop(id)
        else:
            log.critical(f"Index '{id}' out of bound (length = {len(self.names)})", exc_info=1)

    def dumps(self) -> str:
        """
        Serialize this data structure to a JSON formatted str.

        Returns:
            str: JSON stringified data
        """

        data = {
            "names": self.names,
            "units": self.units,
            "ranges": [data.dumps() for data in self.ranges],
        }

        return json.dumps(data)

    def get(self, id: Union[str, int], prop: str = "") -> Union[PointDataInformation, str, ValueRange, None]:
        """
        Return information about point data at the given index.

        Args:
            id (Union[str, int]): can be the index or the name of point data
            prop (str, optional): name of a specific property to get. If not set, return all. Defaults to "".

        Returns:
            Union[PointDataInformation, str, ValueRange, None]: information on point data.
        """

        # Get id of the variable
        if isinstance(id, str):
            try:
                id = self.names.index(id)
            except ValueError:
                log.critical(f"Unkonw id {id}", exc_info=1)
                return None

        # Check is correct
        if id < self.length():

            # Return all information
            if not prop:
                return PointDataInformation(self.names[id], self.units[id], self.ranges[id])

            # Return specific information
            elif prop in ['NAME', 'UNIT', 'RANGE']:
                if prop == 'NAME':
                    return self.names[id]
                if prop == 'UNIT':
                    return self.units[id]
                if prop == 'RANGE':
                    return self.ranges[id]

            else:
                log.critical(f"Property '{prop}' is undefined", exc_info=1)
                return None

        else:
            log.critical(f"Index '{id}' out of bound (length = {len(self.names)})", exc_info=1)
            return None

    def append(self, name: str = 'NONE', unit: str = "", range: ValueRange = ValueRange(), data: dict = None) -> None:
        """
        Append new point data to the data structure.

        Args:
            name (str, optional): name. Defaults to "".
            unit (str, optional): unit. Defaults to "".
            range (ValueRange, optional): value range. Defaults to ValueRange().
            data (dict, optional): data. Defaults to None.
        """

        # Check if append by data
        if data is not None:
            self.names.append(data.get("name", "NONE"))
            self.units.append(data.get("unit", ""))
            self.ranges.append(data.get("range", ValueRange()))

        else:
            self.names.append(name)
            self.units.append(unit)
            self.ranges.append(deepcopy(range))

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        output = "Point data:\n"
        output += f"NAMES: {self.names}\n"
        output += f"UNITS: {self.units}\n"
        return output
