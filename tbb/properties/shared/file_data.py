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

        self.module = ''
        self.file = None
        self.nb_vars = 0
        self.nb_time_points = 0
        self.vars = VariablesInformation()

    def update_var_range(self, name: str, shape: str, scope: str = 'LOCAL',
                         data: Union[np.ndarray, tuple, None] = None) -> None:
        """
        Update variable information (value ranges).

        Args:
            name (str): name of the variable to update
            shape (str): type of the variable. Enum in ['SCALAR', 'VECTOR'].
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

            if shape == 'SCALAR':
                self.vars.ranges[id][scope.lower()] = {"min": float(np.min(data)), "max": float(np.max(data))}

            if shape == 'VECTOR':
                minima, maxima = [], []

                for i in range(data.shape[1]):
                    minima.append(float(np.min(data[:, i])))
                    maxima.append(float(np.max(data[:, i])))

                self.vars.ranges[id][scope.lower()] = {"min": minima, "max": maxima}

        # Update global information
        if scope == 'GLOBAL':
            self.vars.ranges[id][scope.lower()] = data
