# <pep8 compliant>
from typing import Union
from pyvista import OpenFOAMReader, POpenFOAMReader, UnstructuredGrid
import logging
log = logging.getLogger(__name__)
import numpy as np

from tbb.properties.utils import VariablesInformation


class TBB_OpenfoamTemporaryData():
    """Hold temporary data for the OpenFOAM module."""

    # str: name of the module
    module_name = "OpenFOAM"
    #: Union[OpenFOAMReader, POpenFOAMReader]: file reader
    file_reader = None
    #: UnstructuredGrid: 'internalMesh' from data
    raw_mesh = None
    #: UnstructuredGrid: lest generated mesh
    mesh = None
    #: int: current time point
    time_point = 0
    #: int: number of time points
    nb_time_points = 1
    #: VariablesInformation: Information on variables
    vars_info = VariablesInformation()

    def __init__(self, file_reader: Union[OpenFOAMReader, POpenFOAMReader]):
        """Init method of the class."""

        self.module_name = "OpenFOAM"
        self.file_reader = file_reader

        # Load data
        self.set_active_time_point(0)
        self.mesh = self.file_reader.read()["internalMesh"]
        self.nb_time_points = self.file_reader.number_time_points

    def set_active_time_point(self, time_point: int) -> None:
        """
        Update file reader, raw mesh and variables information.

        Args:
            time_point (int): time point to set as active time point.
        """

        try:
            self.file_reader.set_active_time_point(time_point)
            self.raw_mesh = self.file_reader.read()["internalMesh"]
            self.time_point = time_point
        except ValueError:
            log.critical("Caught exception during update", exc_info=1)
            return

        # Generate vars_info
        self.vars_info.clear()
        for name in self.raw_mesh.point_data.keys():
            data = self.raw_mesh.point_data[name]
            type = 'SCALAR' if len(data.shape) == 1 else 'VECTOR'
            dim = 1 if len(data.shape) == 1 else data.shape[1]
            if type == 'VECTOR':
                min = []
                max = []
                for i in range(dim):
                    min.append(float(np.min(np.array(data[:, i]))))
                    max.append(float(np.max(np.array(data[:, i]))))
            elif type == 'SCALAR':
                min = float(np.min(np.array(data)))
                max = float(np.max(np.array(data)))

            ranges = {"local": {"min": min, "max": max}, "global": {"min": None, "max": None}}

            self.vars_info.append(name, unit="", range=ranges, type=type, dim=dim)

    def is_ok(self) -> bool:
        """
        Check if temporary data still hold data (data are not None).

        Returns:
            bool: ``True`` if everything is ok
        """
        return self.file_reader is not None and self.raw_mesh is not None and self.mesh is not None
