# <pep8 compliant>
from __future__ import annotations
import logging
log = logging.getLogger(__name__)

import numpy as np
from pathlib import Path
from typing import Union
from copy import deepcopy
from pyvista import POpenFOAMReader, UnstructuredGrid, PolyData

from nimphs.properties.shared.file_data import FileData
from nimphs.properties.openfoam.import_settings import NIMPHS_OpenfoamImportSettings


class OpenfoamFileData(FileData):
    """Hold file data for the OpenFOAM module."""

    #: UnstructuredGrid: 'internalMesh' from data
    raw_mesh: UnstructuredGrid = None
    #: PolyData: lest generated mesh
    mesh: PolyData = None
    #: bool: Indicate whether triangulation should be applied or not
    tiangulate: bool = False
    #: int: current time point
    time_point: int = 0
    #: bool: indicate if the skip_zero_time property has changed
    skip_zero_has_changed: bool = False

    def __init__(self, file_path: str, settings: Union[NIMPHS_OpenfoamImportSettings, None]) -> None:
        """
        Init method of the class.

        Args:
            file_path (str): file to the path to load
            settings (Union[NIMPHS_OpenfoamImportSettings, None]): OpenFOAM import settings
        """

        super().__init__()  # Must be called first (otherwise it will erase self.file content)

        # Try to load the given file
        if not self.load_file(file_path):
            raise IOError(f"Unable to read the given file {file_path}")

        # Set common settings
        self.time_point = 0
        self.module = 'OpenFOAM'
        self.skip_zero_has_changed = False

        # Load data
        self.update_import_settings(settings)
        self.update_data(self.time_point)
        self.init_point_data_manager()

    def copy(self, other: OpenfoamFileData) -> None:
        """
        Copy important information from the given instance of file data.

        Args:
            other (NIMPHS_OpenfoamFileData): OpenFOAM file data
        """

        self.module = other.module
        self.nb_time_points = other.nb_time_points
        self.vars = deepcopy(other.vars)
        self.triangulate = other.triangulate
        self.time_point = other.time_point

    def get_point_data(self, id: Union[str, int]) -> np.ndarray:
        """
        Get point data from the given id.

        Args:
            id (Union[str, int]): identifier of the variable from which to get data
        """

        channel = id.split('.')[-1]
        name = id[:-2] if channel.isnumeric() else id

        # If these are different, then a clip or something like that has probably been applied
        # So return point data from self.mesh
        if self.mesh.points.size != self.raw_mesh.points.size:
            data = self.mesh.get_array(name=name, preference='point')
            return data[:, int(channel)] if channel.isnumeric() else data

        return self.get_point_data_from_raw(id)

    def get_point_data_from_raw(self, id: Union[str, int]) -> np.ndarray:
        """
        Force to get point data from the raw mesh.

        Args:
            id (Union[str, int]): identifier of the variable from which to get data
        """

        channel = id.split('.')[-1]
        name = id[:-2] if channel.isnumeric() else id

        data = self.raw_mesh.get_array(name=name, preference='point')
        return data[:, int(channel)] if channel.isnumeric() else data

    def update_data(self, time_point: int) -> None:
        """
        Update file data.

        Args:
            time_point (int): time point to read
            io_settings (Union[NIMPHS_OpenfoamImportSettings, None], optional): import settings. Defaults to None.
        """

        # Update mesh
        try:
            self.time_point = time_point
            self.file.set_active_time_point(time_point)
            self.mesh = self.file.read()["internalMesh"]
            self.raw_mesh = self.file.read()["internalMesh"]
        except AttributeError:  # Raised when using wrong case_type
            self.raw_mesh = None
            return
        except ValueError:
            log.critical("Caught exception during update", exc_info=1)
            return

        # The skip_zero_time property can change a lot of things, so we have to update the following data too
        if self.skip_zero_has_changed:
            self.nb_time_points = self.file.number_time_points
            self.init_point_data_manager()
            self.skip_zero_has_changed = False

    def update_import_settings(self, settings: Union[NIMPHS_OpenfoamImportSettings, None]) -> None:
        """
        Update import settings. If none provided, set default settings.

        Args:
            settings (Union[NIMPHS_OpenfoamImportSettings, None]): OpenFOAM import settings
        """

        old = self.file.skip_zero_time

        if settings is not None:
            self.triangulate = settings.triangulate
            self.file.case_type = settings.case_type
            self.file.skip_zero_time = settings.skip_zero_time
            self.file.decompose_polyhedra = settings.decompose_polyhedra
        else:
            self.triangulate = True
            self.file.skip_zero_time = True
            self.file.decompose_polyhedra = True
            self.file.case_type = 'reconstructed'

        # Indicate that the skip_zero_time property has changed
        if old != self.file.skip_zero_time:
            self.skip_zero_has_changed = True

    def is_ok(self) -> bool:
        """
        Check if file data is up (data are not None or empty).

        Returns:
            bool: ``True`` if ok
        """

        return self.file is not None

    def init_point_data_manager(self) -> None:
        """Initialize point data manager (contains variables information)."""

        if self.raw_mesh is not None:

            self.vars.clear()
            for name in self.raw_mesh.point_data.keys():

                data = self.raw_mesh.point_data[name]
                if len(data.shape) > 1:

                    for i in range(data.shape[1]):
                        self.vars.append(f"{name}.{i}")

                    continue

                self.vars.append(name)

    def load_file(self, file_path: str) -> bool:
        """
        Load an OpenFOAM file.

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

        self.file = POpenFOAMReader(file_path)
        return True
