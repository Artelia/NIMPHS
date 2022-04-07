import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from pyvista import OpenFOAMReader
from pathlib import Path

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
        clip = context.scene.tbb_clip
        success, file_reader = load_openfoam_file(self.filepath)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath
        context.scene.tbb_temp_data.update_file_reader(file_reader)

        # Update properties values
        update_properties_values(settings, clip, file_reader.number_time_points - 1)

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
        clip = context.scene.tbb_clip
        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        success, file_reader = load_openfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        context.scene.tbb_temp_data.update_file_reader(file_reader)

        # Update properties values
        update_properties_values(settings, clip, file_reader)

        self.report({"INFO"}, "Reload successfull")
        
        return {"FINISHED"}

def update_properties_values(settings, clip, file_reader):
    # Update settings
    max_time_step =  file_reader.number_time_points - 1
    update_preview_time_step(settings, max_time_step)
    update_start_end_time_steps(settings, max_time_step)
    # Update clip
    update_clip_props(clip, file_reader)

def update_clip_props(clip, file_reader):
    pass

def update_start_end_time_steps(settings, new_max):
    # TODO: this is not working for the momement
    for prop_id in ["start_time", "end_time"]:
        prop = settings.id_properties_ui(prop_id)
        default = getattr(settings, prop_id)
        if new_max < default: default = 0
        prop.update(default=default, min=0, max=new_max)

def update_preview_time_step(settings, new_max):
    # TODO: this is not working for the momement
    prop = settings.id_properties_ui("preview_time_step")
    default = settings.preview_time_step
    if new_max < default: default = 0
    prop.update(default=default, min=0, max=new_max)

def load_openfoam_file(file_path):
    file = Path(file_path)
    if not file.exists():
        return False, None

    # TODO: does this line can throw exceptions? How to manage errors here?
    file_reader = OpenFOAMReader(file_path)
    return True, file_reader