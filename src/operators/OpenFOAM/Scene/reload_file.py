# <pep8 compliant>
from bpy.types import Operator
import time

from ..utils import load_openopenfoam_file, update_properties_values


class TBB_OT_OpenFOAMReloadFile(Operator):
    bl_idname = "tbb.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload the selected file"

    def execute(self, context):
        settings = context.scene.tbb_openfoam_settings

        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        start = time.time()
        success, file_reader = load_openopenfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        # Update properties values
        update_properties_values(context, file_reader)

        # Update temp data
        context.scene.tbb_openfoam_tmp_data.update(file_reader, settings["preview_time_point"])
        settings.create_sequence_is_running = False

        print("Reload::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Reload successfull")

        return {"FINISHED"}
