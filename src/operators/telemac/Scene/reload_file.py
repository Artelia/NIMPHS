# <pep8 compliant>
from bpy.types import Operator, Context
import time

from ..utils import update_settings_dynamic_props


class TBB_OT_TelemacReloadFile(Operator):
    """
    Reload the selected file (update properties and temporary data).
    """

    bl_idname = "tbb.reload_telemac_file"
    bl_label = "Reload"
    bl_description = "Reload the selected file"

    def execute(self, context: Context) -> set:
        """
        Reload the selected file.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb_telemac_settings
        tmp_data = context.scene.tbb_telemac_tmp_data

        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        start = time.time()
        # Read the file and update temporary data
        try:
            tmp_data.update(settings.file_path)
        except Exception as error:
            print("ERROR::TBB_OT_TelemacImportFile: " + str(error))
            self.report({"ERROR"}, "An error occurred during import")
            return {"FINISHED"}

        # Update properties values
        update_settings_dynamic_props(context)

        print("Reload::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Reload successfull")

        return {"FINISHED"}
