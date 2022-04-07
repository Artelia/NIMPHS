class TBB_temporary_data():
    file_reader = None
    file_data = None
    mesh_data = None

    def __init__(self, file_reader=None, file_data=None, mesh_data=None):
        self.file_reader = file_reader
        self.file_data = file_data
        self.mesh_data = mesh_data

    def update_file_reader(self, new_file_reader):
        self.file_reader = new_file_reader
        self.file_data = self.file_reader.read()
        self.mesh_data= self.file_data["internalMesh"]