# <pep8 compliant>
from .serafin import Serafin

import numpy as np


class TBB_TelemacTemporaryData():
    """
    Hold temporary data for the TELEMAC module.
    """

    #: Serafin: TELEMAC file
    file = None
    #: np.array: Vertices of the mesh
    vertices = None
    #: np.array: Faces of the mesh
    faces = None

    def update(self, file_path: str) -> None:
        """
        Update temporary data by reading the file

        :param file_path: path to the TELEMAC file
        :type file_path: str
        """

        self.file = Serafin(file_path, read_time=True)

        nb_vertices = len(self.file.x)
        nb_triangles = int(len(self.file.ikle) / 3)

        # Construct vertices array
        self.vertices = np.vstack((self.file.x, self.file.y)).T
        self.vertices = np.hstack((self.vertices, np.zeros((nb_vertices, 1))))

        # Construct faces array
        self.faces = np.array(self.file.ikle).reshape((nb_triangles, 3))

    def is_ok(self) -> bool:
        """
        Return if temporary data still hold data (data are not None).

        :rtype: bool
        """
        return self.file is not None and self.vertices is not None and self.faces is not None
