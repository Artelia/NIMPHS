from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from .utils import load_openfoam_file, update_properties_values, generate_preview_object

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
        success, file_reader = load_openfoam_file(self.filepath)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Update properties values
        update_properties_values(context, file_reader)

        # Update temp data
        context.scene.tbb_temp_data.update(file_reader, settings["preview_time_point"])

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while on large meshes.
        try:
            preview_mesh = context.scene.tbb_temp_data.mesh_data.extract_surface()
            generate_preview_object(preview_mesh, context)
        except Exception as error:
            print("ERROR::TBB_OT_ImportFoamFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

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

        success, file_reader = load_openfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        # Update properties values
        update_properties_values(context, file_reader)

        # Update temp data
        context.scene.tbb_temp_data.update(file_reader, settings["preview_time_point"])

        settings.create_sequence_is_running = False

        self.report({"INFO"}, "Reload successfull")
        
        return {"FINISHED"}