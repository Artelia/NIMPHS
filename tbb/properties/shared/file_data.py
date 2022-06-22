# <pep8 compliant>
import numpy as np
from typing import Union
from pyvista import POpenFOAMReader

from tbb.properties.telemac.serafin import Serafin
from tbb.properties.utils import VariablesInformation


class TBB_FileData():
    """Base class to manage file data for all modules."""

    #: str: Name of the module
    module: str = ''
    #: Union[Serafin, POpenFOAMReader]: File reader
    file: Union[Serafin, POpenFOAMReader] = None
    #: int: Number of available variables
    nb_vars: int = 0
    #: int: Number of readable time points
    nb_time_points: int = 0
    #: VariablesInformation: Information on variables
    vars: VariablesInformation = None

    def __init__(self) -> None:
        """Init method of the class."""

        self.module = ""
        self.file = None
        self.nb_vars = 0
        self.nb_time_points = 0
        self.vars = VariablesInformation()

    def get_point_data(self, _id: Union[str, int]) -> np.ndarray:
        """
        Get point data from the given id.

        Args:
            _id (Union[str, int]): identifier of the variable from which to get data
        """

        pass

    def update_vars(self, vars: list[dict], scope: str = 'LOCAL') -> None:
        """
        Update variables information (value ranges).

        Args:
            vars (list[dict]): list of variables to update {"name": name, "data": data or None}
            scope (str): indicate which information to update. Enum in ['LOCAL', 'GLOBAL'].
        """

        for info in vars:
            # Get data if not provided
            if info["data"] is None:
                info["data"] = self.get_point_data(info["name"])

            id = self.vars.names.index(info["name"])

            # Update local information
            if scope == 'LOCAL':
                self.vars.ranges[id][scope.lower()] = {"min": np.min(info["data"]), "max": np.max(info["data"])}

    def is_ok(self) -> bool:
        """
        Check if file data is up (data are not None or empty).

        Returns:
            bool: ``True`` if ok
        """

        pass
