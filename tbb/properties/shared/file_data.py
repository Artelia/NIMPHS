# <pep8 compliant>
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

    def update(self, _time_point: int) -> None:
        """
        Update file data.

        Args:
            _time_point (int): time point to use for the update
        """

        pass

    def is_ok(self) -> bool:
        """
        Check if file data is up (data are not None or empty).

        Returns:
            bool: ``True`` if ok
        """
        pass
