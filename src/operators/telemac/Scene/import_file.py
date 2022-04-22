# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, Context
from bpy.props import StringProperty

import time

from ..utils import update_settings_dynamic_props


class TBB_OT_TelemacImportFile(Operator, ImportHelper):
    """
    Import a TELEMAC file. This operator manages the file browser and its filtering options.
    """

    bl_idname = "tbb.import_telemac_file"
    bl_label = "Import"
    bl_description = "Import a TELEMAC file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.slf",  # multiple allowed types: "*.slf;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context: Context) -> set:
        """
        Import the selected file. It also generates the preview object.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb_telemac_settings
        tmp_data = context.scene.tbb_telemac_tmp_data
        start = time.time()

        # Read the file and update temporary data
        try:
            tmp_data.update(self.filepath)
        except Exception as error:
            print("ERROR::TBB_OT_TelemacImportFile: " + str(error))
            self.report({"ERROR"}, "An error occurred during import")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Update properties values
        update_settings_dynamic_props(context)

        print("Import::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}
