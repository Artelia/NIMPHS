# <pep8 compliant>
from __future__ import annotations
import logging
log = logging.getLogger(__name__)

import numpy as np
from pathlib import Path
from typing import Union
from copy import deepcopy

from tbb.properties.telemac.serafin import Serafin
from tbb.properties.shared.file_data import TBB_FileData
from tbb.properties.telemac.utils import remove_spaces_telemac_var_name


class TBB_TelemacFileData(TBB_FileData):
    """Hold file data for the TELEMAC module."""

    #: np.ndarray: Vertices of the mesh
    vertices: np.ndarray = None

    #: np.ndarray: Faces of the mesh
    faces: np.ndarray = None

    #: int: Number of planes
    nb_planes: int = 0

    #: int: Number of vertices
    nb_vertices: int = 0

    #: int: Number of triangles
    nb_triangles: int = 0

    #: np.ndarray: Data
    data: np.ndarray = None

    def __init__(self, file_path: str) -> None:
        """
        Init method of the class.

        Args:
            file_path (str): path to the TELEMAC file
        """

        super().__init__()  # Must be called first (otherwise it will erase self.file content)

        if not self.load_file(file_path):
            raise IOError(f"Unable to read the given file {file_path}")

        # Set common settings
        self.module = 'TELEMAC'

        self.file.get_2d()  # Read mesh
        self.data = self.file.read(self.file.temps[0])  # Read time step

        self.nb_planes = self.file.nplan

        self.nb_vertices = self.file.npoin2d if self.is_3d() else self.file.npoin
        self.nb_triangles = len(self.file.ikle2d) if self.is_3d() else int(len(self.file.ikle) / 3)
        self.nb_vars = self.file.nbvar

        self.nb_time_points = self.file.nb_pdt

        # Construct vertices array
        self.vertices = np.vstack((self.file.x[:self.nb_vertices], self.file.y[:self.nb_vertices])).T

        # Construct faces array
        # Note: '-1' to remove the '+1' offset in the ikle array
        if not self.is_3d():
            self.faces = (np.array(self.file.ikle) - 1).reshape((self.nb_triangles, 3))
        else:
            self.faces = self.file.ikle2d

        # Initialize variables information
        for var_name in self.file.nomvar:
            # Note: var_name is always 32 chars long with 16 chars for the name and 16 for the unit name
            name = remove_spaces_telemac_var_name(var_name[:16])
            unit = remove_spaces_telemac_var_name(var_name[16:])
            self.vars.append(name=name, unit=unit)

    def copy(self, other: TBB_TelemacFileData) -> None:
        """
        Copy important information from the given instance of file data.

        Args:
            other (TBB_TelemacFileData): TELEMAC file data
        """

        self.vars = deepcopy(other.vars)

    def get_point_data(self, id: Union[str, int]) -> np.ndarray:
        """
        Get point data from the given id.

        Args:
            id (Union[str, int]): identifier of the variable from which to get data
        """

        if isinstance(id, str):
            id = self.vars.names.index(id)

        return self.data[id]

    def update_data(self, time_point: int) -> None:
        """
        Update file data.

        Args:
            time_point (int): time point to read
        """

        self.data = self.read(time_point)

    def is_ok(self) -> bool:
        """
        Check if file data is up (data are not None or empty).

        Returns:
            bool: ``True`` if ok
        """

        return self.file is not None and self.vertices is not None and self.faces is not None

    def is_3d(self) -> bool:
        """
        Indicate if the file is from a 3D simulation.

        Returns:
            bool: state
        """

        return self.nb_planes > 1

    def read(self, time_point: int = 0) -> np.ndarray:
        """
        Read and return data at the given time point.

        Args:
            time_point (int, optional): time point from which to read data. Defaults to 0.

        Raises:
            ValueError: if the time point does not exist

        Returns:
            np.ndarray: data
        """

        if time_point > self.nb_time_points or time_point < 0:
            raise ValueError("Undefined time point (" + str(time_point) + ")")

        return self.file.read(self.file.temps[time_point])

    def load_file(self, file_path: str) -> bool:
        """
        Load TELEMAC (Serafin) file.

        Args:
            file_path (str): path to the file to load

        Returns:
            bool: success
        """

        path = Path(file_path)
        if not path.exists():
            log.error(f"Unknown path: {file_path}")
            return False
        elif path.is_dir():
            log.error("Cannot open files from directories")
            return False

        self.file = Serafin(file_path, read_time=True)
        return True