# <pep8 compliant>
from bpy.types import Operator
import time

from ..utils import load_openopenfoam_file, update_settings_dynamic_props
from ....properties.openfoam.utils import encode_value_ranges, encode_scalar_names


class TBB_OT_OpenfoamReloadFile(Operator):
    bl_idname = "tbb.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload the selected file"

    def execute(self, context):
        settings = context.scene.tbb_openfoam_settings
        tmp_data = context.scene.tbb_openfoam_tmp_data

        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        start = time.time()
        success, file_reader = load_openopenfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        # Update properties values
        update_settings_dynamic_props(context, file_reader)

        # Update temp data
        tmp_data.update(file_reader, settings["preview_time_point"])
        settings.clip.scalar.value_ranges = encode_value_ranges(tmp_data.mesh)
        settings.clip.scalar.list = encode_scalar_names(tmp_data.mesh)
        settings.create_sequence_is_running = False

        print("Reload::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Reload successfull")

        return {"FINISHED"}
