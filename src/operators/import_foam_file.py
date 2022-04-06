import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from pyvista import OpenFOAMReader
from pathlib import Path

def load_openfoam_file(file_path, preview_time_step, panel):
    # TODO: does these lines can throw exceptions? How to manage errors here?
    panel.file_reader = OpenFOAMReader(file_path)
    panel.file_reader.set_active_time_point(preview_time_step)
    panel.openfoam_data = panel.file_reader.read()
    panel.openfoam_mesh = panel.openfoam_data["internalMesh"]

class TBB_OT_ImportFoamFile(Operator, ImportHelper):
    bl_idname="tbb.import_foam_file"
    bl_label="Import"
    bl_description="Import an OpenFoam file"

    filter_glob: StringProperty(
        default="*.foam", # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        # If the settings properties have not been created yet
        settings = None
        try:
            settings = context.scene.tbb_settings[0]
        except IndexError as error:
            print(error)
            settings = context.scene.tbb_settings.add()

        file_path = Path(self.filepath)
        if not file_path.exists():
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        load_openfoam_file(settings.file_path, settings.preview_time_step, bpy.types.TBB_PT_MainPanel)

        # Forces to redraw the view (magic trick)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        # Because the operation can take a while, prevent the user that it is finished
        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}

class TBB_OT_ReloadFoamFile(Operator):
    bl_idname="tbb.reload_foam_file"
    bl_label="Reload"
    bl_description="Reload the selected file"

    def execute(self, context):
        settings = None
        try:
            settings = context.scene.tbb_settings[0]
        except IndexError as error:
            # This error means that the settings have not been created yet.
            # It can be resolved by importing a new file.
            print(error)
            self.report({"ERROR"}, "Please import a file first")
            return {"FINISHED"}

        load_openfoam_file(settings.file_path, settings.preview_time_step, bpy.types.TBB_PT_MainPanel)

        # Because the operation can take a while, prevent the user that it is finished
        self.report({"INFO"}, "File successfully imported")
        
        return {"FINISHED"}