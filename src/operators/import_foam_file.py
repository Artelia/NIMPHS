from email.policy import default
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from pyvista import OpenFOAMReader
from pathlib import Path

def update_preview_time_step(settings, new_max):
    # TODO: this is not working for the momement
    prop = settings.id_properties_ui("preview_time_step")
    default = settings.preview_time_step
    if new_max < default: default = 0
    prop.update(default=default, min=0, max=new_max)

def load_openfoam_file(file_path, preview_time_step, panel):
    file = Path(file_path)
    if not file.exists():
        return False, None

    # TODO: does these lines can throw exceptions? How to manage errors here?
    panel.file_reader = OpenFOAMReader(file_path)
    # panel.file_reader.set_active_time_point(preview_time_step)
    # panel.openfoam_data = panel.file_reader.read()
    # panel.openfoam_mesh = panel.openfoam_data["internalMesh"]
    return True, panel.file_reader

class TBB_OT_ImportFoamFile(Operator, ImportHelper):
    bl_idname="tbb.import_foam_file"
    bl_label="Import"
    bl_description="Import an OpenFoam file"

    filter_glob: StringProperty(
        default="*.foam", # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        settings = context.scene.tbb_settings
        success, file_reader = load_openfoam_file(self.filepath, settings.preview_time_step, bpy.types.TBB_PT_MainPanel)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Set the new preview_time_step upper bound
        update_preview_time_step(settings, file_reader.number_time_points - 1)

        # Forces to redraw the view (magic trick)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}

class TBB_OT_ReloadFoamFile(Operator):
    bl_idname="tbb.reload_foam_file"
    bl_label="Reload"
    bl_description="Reload the selected file"

    def execute(self, context):
        settings = context.scene.tbb_settings
        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        success, file_reader = load_openfoam_file(settings.file_path, settings.preview_time_step, bpy.types.TBB_PT_MainPanel)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        # Set the new preview_time_step upper bound
        update_preview_time_step(settings, file_reader.number_time_points - 1)

        self.report({"INFO"}, "Reload successfull")
        
        return {"FINISHED"}


# rna_ui = bpy.context.scene.tbb_settings.get("_RNA_UI")