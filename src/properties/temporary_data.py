class TBB_temporary_data():
    file_reader = None
    file_data = None
    mesh_data = None
    time_step = 0

    def __init__(self, file_reader=None, file_data=None, mesh_data=None):
        self.file_reader = file_reader
        self.file_data = file_data
        self.mesh_data = mesh_data

    def update(self, new_file_reader, time_step=0, new_file_data=None, new_mesh_data=None):
        self.file_reader = new_file_reader
        self.time_step = time_step
        try:
            self.file_reader.set_active_time_point(time_step)
        except ValueError as error:
            print("ERROR::TBB_temporary_data: " + error)

        if new_file_data == None:
            self.file_data = self.file_reader.read()
        else:
            self.file_data = new_file_data

        if new_mesh_data == None:
            self.mesh_data = self.file_data["internalMesh"]
        else:
            self.mesh_data = new_mesh_data

    def is_ok(self):
        return self.file_reader != None and self.file_data != None and self.mesh_data != None