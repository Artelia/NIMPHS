# <pep8 compliant>
from typing import Union
from pyvista import OpenFOAMReader, POpenFOAMReader, DataSet, UnstructuredGrid
import logging
log = logging.getLogger(__name__)
import numpy as np

from tbb.properties.utils import append_vars_info, clear_vars_info


class TBB_OpenfoamTemporaryData():
    """Hold temporary data for the OpenFOAM module."""

    # str: name of the module
    module_name = "OpenFOAM"
    #: Union[OpenFOAMReader, POpenFOAMReader]: file reader
    file_reader = None
    #: Dataset: data read from the file_reader at time_point
    data = None
    # UnstructuredGrid: 'internalMesh' from data
    mesh = None
    #: int: current time point
    time_point = 0
    #: int: number of time points
    nb_time_points = 1
    #: dict: Information on variables
    vars_info = {"names": [], "units": [], "ranges": [], "types": [], "dimensions": []}

    def __init__(self, file_reader: Union[OpenFOAMReader, POpenFOAMReader] = None,
                 new_data: DataSet = None, new_mesh: UnstructuredGrid = None):
        """
        Init method of the class.

        Args:
            file_reader (Union[OpenFOAMReader, POpenFOAMReader], optional): new file reader. Defaults to None.
            new_data (DataSet, optional): new dataset. Defaults to None.
            new_mesh (UnstructuredGrid, optional): new mesh. Defaults to None.
        """

        self.module_name = "OpenFOAM"
        self.file_reader = file_reader
        self.data = new_data
        self.mesh = new_mesh
        self.time_point = 0
        self.nb_time_points = 1

    def update(self, new_file_reader: Union[OpenFOAMReader, POpenFOAMReader], time_point: int = 0,
               new_data: DataSet = None, new_mesh: UnstructuredGrid = None) -> None:
        """
        Update temporary data with the given data.

        Args:
            new_file_reader (OpenFOAMReader): new file reader
            time_point (int, optional): current time point. Defaults to 0.
            new_data (DataSet, optional): new dataset. Defaults to None.
            new_mesh (UnstructuredGrid, optional): new mesh. Defaults to None.
        """

        self.file_reader = new_file_reader
        self.time_point = time_point
        self.nb_time_points = self.file_reader.number_time_points

        try:
            self.file_reader.set_active_time_point(time_point)
        except ValueError:
            log.error("Exception caught setting new active time point", exc_info=1)

        if new_data is None:
            self.data = self.file_reader.read()
        else:
            self.data = new_data

        if new_mesh is None:
            self.mesh = self.data["internalMesh"]
        else:
            self.mesh = new_mesh

        # Generate vars_info
        clear_vars_info(self.vars_info)
        for name in self.mesh.point_data.keys():
            data = self.mesh.point_data[name]
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

            print(ranges)
            append_vars_info(self.vars_info, name, unit="", range=ranges, type=type, dim=dim)

    def is_ok(self) -> bool:
        """
        Check if temporary data still hold data (data are not None).

        Returns:
            bool: ``True`` if everything is ok
        """
        return self.file_reader is not None and self.data is not None and self.mesh is not None
