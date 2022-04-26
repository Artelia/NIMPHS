# <pep8 compliant>
from .serafin import Serafin
from .utils import remove_spaces_telemac_var_name

import numpy as np


class TBB_TelemacTemporaryData():
    """
    Hold temporary data for the TELEMAC module.
    """

    #: Serafin: TELEMAC file
    file = None
    #: np.ndarray: Vertices of the mesh
    vertices = None
    #: np.ndarray: Faces of the mesh
    faces = None
    #: int: Number of variables
    nb_vars = 0
    #: int: Number of time points
    nb_time_points = 0
    #: dict: Information on variables (names and units)
    variables_info = {"names": [], "units": []}
    #: int: Number of planes
    nb_planes = 0
    #: int: Number of vertices
    nb_vertices = 0
    #: int: Number of triangles
    nb_triangles = 0
    # bool: True if the file contains more than one plane
    is_3d = False

    def __init__(self) -> None:
        self.file = None
        self.vertices = None
        self.faces = None
        self.nb_vars = 0
        self.nb_time_points = 0
        self.variables_info = {"names": [], "units": []}
        self.nb_planes = 0
        self.nb_vertices = 0
        self.nb_triangles = 0

    def update(self, file_path: str) -> None:
        """
        Update temporary data by reading the file.

        :param file_path: path to the TELEMAC file
        :type file_path: str
        """

        self.file = Serafin(file_path, read_time=True)
        self.file.get_2d()
        self.file.read(self.file.temps[0])

        self.nb_vertices = len(self.file.x)
        self.nb_triangles = int(len(self.file.ikle) / 3)
        self.nb_vars = self.file.nbvar
        self.nb_time_points = self.file.nb_pdt
        self.nb_planes = self.file.nplan
        self.is_3d = self.file.nplan > 1

        # Construct vertices array
        self.vertices = np.vstack((self.file.x, self.file.y)).T

        # Construct faces array
        # '-1' to remove the '+1' offset in the ikle array
        self.faces = (np.array(self.file.ikle) - 1).reshape((self.nb_triangles, 3))

        # Clear old variables information
        self.variables_info["names"].clear()
        self.variables_info["units"].clear()
        # Construct variables information data
        for var_info in self.file.nomvar:
            # var_info is always 32 chars long with 16 chars for the name and 16 for the unit name
            name = remove_spaces_telemac_var_name(var_info[:16])
            unit = remove_spaces_telemac_var_name(var_info[16:])
            self.variables_info["names"].append(name)
            self.variables_info["units"].append(unit)

    def is_ok(self) -> bool:
        """
        Return if temporary data still hold data (data are not None).

        :rtype: bool
        """
        return self.file is not None and self.vertices is not None and self.faces is not None

    def read(self, time_point: int = 0) -> np.ndarray:
        """
        Read and return data at the given time point.

        :param time_point: time point to read data, defaults to 0
        :type time_point: int, optional
        :raises ValueError: if the time point does not exist
        :return: read data
        :rtype: np.ndarray
        """

        if time_point > self.nb_time_points or time_point < 0:
            raise ValueError("Undefined time point (" + str(time_point) + ")")

        return self.file.read(self.file.temps[time_point])

    def get_data_from_var_name(self, var_name: str, time_point: int, output_shape: str = 'COL') -> np.ndarray:
        """_summary_

        :param var_name: name of the variable
        :type var_name: str
        :param time_point: time point to read data
        :type time_point: int
        :param output_shape: shape of the output, enum in ['COL', 'ROW']
        :type output_shape: str
        :raises error: if something went wrong when reading data
        :raises ValueError: if the given variable name does not exist
        :return: read data
        :rtype: np.ndarray
        """

        try:
            data = self.read(time_point)
        except Exception as error:
            raise error

        # Get the id of the variable name if Serafin.nomvar
        var_id = np.inf
        for name, id in zip(self.variables_info["names"], range(self.nb_vars)):
            if var_name == name:
                var_id = id

        if var_id == np.inf:
            raise NameError("The given variable name '" + str(var_name) + "' is not defined")

        # By default, always output with 'COL' shape, even the given shape is not defined.
        if output_shape not in ['ROW', 'COL']:
            print("WARNING::get_data_from_var_name: unknown output_shape '" +
                  str(output_shape) + "', default output to 'COL' mode.")
        if output_shape == 'ROW':
            return data[var_id]
        else:
            return np.array(data[var_id]).reshape(data[var_id].shape[0], 1)
