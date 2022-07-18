# <pep8 compliant>
import numpy as np
from typing import Union
from pyvista import POpenFOAMReader

from tbb.properties.telemac.serafin import Serafin
from tbb.properties.utils.point_data_manager import PointDataManager


class TBB_FileData():
    """Base class to manage file data for all modules."""

    #: str: Name of the module
    module: str = ''

    #: Union[Serafin, POpenFOAMReader]: File reader
    file: Union[Serafin, POpenFOAMReader] = None

    #: int: Number of readable time points
    nb_time_points: int = 0

    #: PointDataManager: Information on variables
    vars: PointDataManager = None

    def __init__(self) -> None:
        """Init method of the class."""

        self.module = ''
        self.file = None
        self.nb_time_points = 0
        self.vars = PointDataManager()

    def get_point_data(self, _id: Union[str, int]) -> np.ndarray:
        """
        Get point data from the given id. Overriden id derived classes.

        Args:
            _id (Union[str, int]): identifier of the variable from which to get data
        """

        pass

    def update_var_range(self, name: str, scope: str = 'LOCAL', data: Union[np.ndarray, tuple, None] = None) -> None:
        """
        Update point data information (value ranges).

        Args:
            name (str): name of the variable to update
            scope (str, optional): indicate which information to update. Enum in ['LOCAL', 'GLOBAL'].\
                                   Defaults to 'LOCAL'.
            data (Union[np.ndarray, tuple, None], optional): data corresponding to the given variable\
                                                             or min / max values. Defaults to None.
        """

        # Get id of the variable to update in VariablesInformation
        id = self.vars.names.index(name)

        # Update local information
        if scope == 'LOCAL':

            # Get data if not provided
            if data is None:
                data = self.get_point_data(name)
            
            self.vars.ranges[id].minL = float(np.min(data))
            self.vars.ranges[id].maxL = float(np.max(data))

        # Update global information
        if scope == 'GLOBAL':
            self.vars.ranges[id].minG = data["min"]
            self.vars.ranges[id].maxG = data["max"]
