# <pep8 compliant>
from pyvista import OpenFOAMReader, DataSet, UnstructuredGrid


class TBB_OpenfoamTemporaryData():
    """
    Hold temporary data for the OpenFOAM module.
    """

    #: OpenFOAMReader: file reader
    file_reader = None
    #: Dataset: data read from the file_reader at time_point
    data = None
    # UnstructuredGrid: 'internalMesh' from data
    mesh = None
    #: int: current time point
    time_point = 0

    def __init__(self, file_reader: OpenFOAMReader = None, new_data: DataSet = None, new_mesh: UnstructuredGrid = None):
        self.file_reader = file_reader
        self.data = new_data
        self.mesh = new_mesh

    def update(self, new_file_reader: OpenFOAMReader, time_point: int = 0, new_data: DataSet = None,
               new_mesh: UnstructuredGrid = None) -> None:
        """
        Update temporary data with the given data.

        :type new_file_reader: OpenFOAMReader
        :type time_point: int, optional
        :type new_data: DataSet, optional
        :type new_mesh: UnstructuredGrid, optional
        """

        self.file_reader = new_file_reader
        self.time_point = time_point

        try:
            self.file_reader.set_active_time_point(time_point)
        except ValueError as error:
            print("ERROR::TBB_OpenfoamTemporaryData: " + str(error))

        if new_data is None:
            self.data = self.file_reader.read()
        else:
            self.data = new_data

        if new_mesh is None:
            self.mesh = self.data["internalMesh"]
        else:
            self.mesh = new_mesh

    def is_ok(self) -> bool:
        """
        Return if temporary data still hold data (data are not None).

        :rtype: bool
        """
        return self.file_reader is not None and self.data is not None and self.mesh is not None
