# <pep8 compliant>
from pyvista import OpenFOAMReader


class TBB_OpenFOAMTemporaryData():
    file_reader = None
    data = None
    mesh = None
    time_point = 0

    def __init__(self, file_reader: OpenFOAMReader = None, new_data=None, new_mesh=None):
        self.file_reader = file_reader
        self.data = new_data
        self.mesh = new_mesh

    def update(self, new_file_reader: OpenFOAMReader, time_point: int = 0, new_data=None, new_mesh=None) -> None:
        self.file_reader = new_file_reader
        self.time_point = time_point

        try:
            self.file_reader.set_active_time_point(time_point)
        except ValueError as error:
            print("ERROR::TBB_OpenFOAMTemporaryData: " + str(error))

        if new_data is None:
            self.data = self.file_reader.read()
        else:
            self.data = new_data

        if new_mesh is None:
            self.mesh = self.data["internalMesh"]
        else:
            self.mesh = new_mesh

    def is_ok(self) -> bool:
        return self.file_reader is not None and self.data is not None and self.mesh is not None
