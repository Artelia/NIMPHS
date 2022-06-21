# <pep8 compliant>
import time
import numpy as np

import logging
log = logging.getLogger(__name__)

from tbb.properties.telemac.serafin import Serafin
from tbb.properties.shared.file_data import TBB_FileData
from tbb.properties.telemac.utils import remove_spaces_telemac_var_name


class TBB_TelemacFileData(TBB_FileData):
    """Hold file data for the TELEMAC module."""

    #: np.ndarray: Vertices of the mesh
    vertices = None
    #: np.ndarray: Faces of the mesh
    faces = None
    #: int: Number of planes
    nb_planes = 0
    #: int: Number of vertices
    nb_vertices = 0
    #: int: Number of triangles
    nb_triangles = 0
    #: np.ndarray: Data
    data = None

    def __init__(self, file_path: str, compute_value_ranges: bool) -> None:
        """
        Init method of the class.

        Args:
            file_path (str): path to the TELEMAC file
            compute_value_ranges (bool): compute value ranges for all the variables
        """
        super().__init__()

        self.module = 'TELEMAC'
        self.file = Serafin(file_path, read_time=True)

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

        # Construct variables information data
        self.vars.clear()
        for var_name, id in zip(self.file.nomvar, range(self.nb_vars)):
            # Note: var_name is always 32 chars long with 16 chars for the name and 16 for the unit name
            name = remove_spaces_telemac_var_name(var_name[:16])
            unit = remove_spaces_telemac_var_name(var_name[16:])

            # Compute value ranges
            if compute_value_ranges:
                value_range = self.compute_var_value_range(id)
                value_range = {"global": {"min": value_range["min"], "max": value_range["max"]}}
            else:
                value_range = self.read(0)[id]
                value_range = {"local": {"min": np.min(value_range), "max": np.max(value_range)}}

            self.vars.append(name=name, unit=unit, range=value_range)

    def update(self, time_point: int) -> None:
        """
        Update file data.

        Args:
            time_point (int): time point to read
        """

        self.data = self.read(time_point)

        # Compute 'local' value ranges
        for id in range(self.nb_vars):
            self.vars.ranges[id]["local"] = {"min": np.min(self.data[id]), "max": np.max(self.data[id])}

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

    def get_data_from_var_name(self, var_name: str, time_point: int, output_shape: str = 'COL') -> np.ndarray:
        """
        Read and return data corresponding to the given variable name.

        Args:
            var_name (str): name of the variable
            time_point (int): time point from which to read data
            output_shape (str, optional): shape of the output. Enum in ['COL', 'ROW']. Defaults to 'COL'.

        Raises:
            error: if something went wrong when reading data
            NameError: if the given variable name does not exist

        Returns:
            np.ndarray: data
        """

        try:
            data = self.read(time_point)
        except Exception as error:
            raise error

        # Get the id of the variable name if Serafin.nomvar
        try:
            var_id = self.vars.names.index(var_name)
        except ValueError:
            raise NameError("The given variable name '" + str(var_name) + "' is not defined")

        # By default, always output with 'COL' shape, even the given shape is not defined.
        if output_shape not in ['ROW', 'COL']:
            log.warning(f"Unknown output shape {output_shape}. Default to 'COL' mode.")
        if output_shape == 'ROW':
            return data[var_id]
        else:
            return np.array(data[var_id]).reshape(data[var_id].shape[0], 1)

    def get_data_from_possible_var_names(self, possible_var_names: list[str],
                                         time_point: int) -> tuple[np.ndarray, str]:
        """
        Get data from the file and check for every possible given names.\
        When one is found, return the associated data.

        Args:
            possible_var_names (list[str]): variable names which could probably be defined in the Serafin file
            time_point (int): time point from which to read data

        Raises:
            error: if an error occurred reading the Serafin file
            NameError: if the possible names are not defined

        Returns:
            tuple[np.ndarray, str]: data, name of the variable which corresponds to the returned data
        """

        z_values = None
        for var_name in possible_var_names:
            try:
                z_values = self.get_data_from_var_name(var_name, time_point)
            except NameError:
                pass
            except Exception as error:
                raise error

            if z_values is not None:
                return z_values, var_name

        if z_values is None:
            raise NameError("Undefined variables " + str(possible_var_names))
        else:
            return z_values, var_name

    def compute_var_value_range(self, var_id: int) -> tuple[float, float]:
        """
        Compute global min / max values of all time points.

        Args:
            var_id (int): variable id

        Returns:
            tuple[float, float]: min, max
        """

        start = time.time()
        min, max = np.inf, -np.inf
        for time_point in range(self.nb_time_points):
            data = self.read(time_point)[var_id]
            new_min, new_max = np.min(data), np.max(data)
            if new_min < min:
                min = new_min
            if new_max > max:
                max = new_max

        self.vars.ranges[var_id]["global"] = {"min": min, "max": max}

        message = f"Compute 'global' var value range for {self.vars.get(var_id, prop='NAME')}"
        log.info(message + "{:.4f}".format(time.time() - start) + "s")
        return (min, max)
