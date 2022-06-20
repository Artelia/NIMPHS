# <pep8 compliant>
from typing import Union
from pyvista import OpenFOAMReader, POpenFOAMReader, UnstructuredGrid
import logging

from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings
log = logging.getLogger(__name__)
import numpy as np

from tbb.properties.utils import VariablesInformation


class TBB_OpenfoamTemporaryData():
    """Hold temporary data for the OpenFOAM module."""

    # str: name of the module
    module_name = "OpenFOAM"
    #: POpenFOAMReader: file reader
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
    #: bool: Indicate
    tiangulate = False

    def __init__(self, file_reader: POpenFOAMReader, io_settings: Union[TBB_OpenfoamImportSettings, None]):
        """Init method of the class."""

        self.module_name = "OpenFOAM"
        self.file_reader = file_reader

        # Load data
        self.update(0, io_settings=io_settings)
        try:
            self.mesh = self.file_reader.read()["internalMesh"]
        except KeyError:  # Raised when using wrong case_type
            self.mesh = None
            return

        self.nb_time_points = self.file_reader.number_time_points

    def update(self, time_point: int, io_settings: Union[TBB_OpenfoamImportSettings, None] = None) -> None:
        """
        Update file reader, raw mesh and variables information.

        Args:
            time_point (int): time point to set as active time point.
        """

        # Update import settings
        if io_settings is not None:
            self.file_reader.decompose_polyhedra = io_settings.decompose_polyhedra
            self.file_reader.case_type = io_settings.case_type
            self.triangulate = io_settings.triangulate
        else:
            self.file_reader.decompose_polyhedra = True
            self.file_reader.case_type = 'reconstructed'
            self.triangulate = True

        # Update mesh
        try:
            self.time_point = time_point
            self.file_reader.set_active_time_point(time_point)
            self.raw_mesh = self.file_reader.read()["internalMesh"]
        except AttributeError:  # Raised when using wrong case_type
            self.raw_mesh = None
            return
        except ValueError:
            log.critical("Caught exception during update", exc_info=1)
            return

        # Update vars_info
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
        return self.file_reader is not None
