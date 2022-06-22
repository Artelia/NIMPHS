# <pep8 compliant>
import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Union
from pyvista import POpenFOAMReader, UnstructuredGrid, PolyData

from tbb.properties.shared.file_data import TBB_FileData
from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings


class TBB_OpenfoamFileData(TBB_FileData):
    """Hold file data for the OpenFOAM module."""

    #: UnstructuredGrid: 'internalMesh' from data
    raw_mesh: UnstructuredGrid = None
    #: PolyData: lest generated mesh
    mesh: PolyData = None
    #: bool: Indicate
    tiangulate: bool = False
    #: int: current time point
    time_point: int = 0

    def __init__(self, file: POpenFOAMReader, io_settings: Union[TBB_OpenfoamImportSettings, None]) -> None:
        """Init method of the class."""

        super().__init__()

        self.module = "OpenFOAM"
        self.file = file

        # Load data
        self.update_data(0, io_settings=io_settings)
        try:
            self.mesh = self.file.read()["internalMesh"]
        except KeyError:  # Raised when using wrong case_type
            self.mesh = None
            return

        self.nb_time_points = self.file.number_time_points

        # Initialize variables information
        for name in self.raw_mesh.point_data.keys():
            data = self.raw_mesh.point_data[name]
            type = 'SCALAR' if len(data.shape) == 1 else 'VECTOR'
            dim = 1 if len(data.shape) == 1 else data.shape[1]
            self.vars.append(name, unit="", range=None, type=type, dim=dim)

    def get_point_data(self, id: Union[str, int]) -> np.ndarray:
        """
        Get point data from the given id.

        Args:
            id (Union[str, int]): identifier of the variable from which to get data
        """

        return self.mesh.get_array(name=id, preference='point')

    def update_data(self, time_point: int, io_settings: Union[TBB_OpenfoamImportSettings, None] = None) -> None:
        """
        Update file data.

        Args:
            time_point (int): time point to read
            io_settings (Union[TBB_OpenfoamImportSettings, None], optional): import settings. Defaults to None.
        """

        # Update import settings
        if io_settings is not None:
            self.file.decompose_polyhedra = io_settings.decompose_polyhedra
            self.file.case_type = io_settings.case_type
            self.triangulate = io_settings.triangulate
        else:
            self.file.decompose_polyhedra = True
            self.file.case_type = 'reconstructed'
            self.triangulate = True

        # Update mesh
        try:
            self.time_point = time_point
            self.file.set_active_time_point(time_point)
            self.raw_mesh = self.file.read()["internalMesh"]
        except AttributeError:  # Raised when using wrong case_type
            self.raw_mesh = None
            return
        except ValueError:
            log.critical("Caught exception during update", exc_info=1)
            return

    def is_ok(self) -> bool:
        """
        Check if file data is up (data are not None or empty).

        Returns:
            bool: ``True`` if ok
        """

        return self.file is not None
