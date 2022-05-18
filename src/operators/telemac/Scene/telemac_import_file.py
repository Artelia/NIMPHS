# <pep8 compliant>
from bpy.props import StringProperty
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper

import time

from src.operators.utils import get_object_dimensions_from_mesh
from src.operators.telemac.utils import generate_preview_objects
from src.operators.utils import update_scene_settings_dynamic_props


class TBB_OT_TelemacImportFile(Operator, ImportHelper):
    """
    Import a TELEMAC file. This operator manages the file browser and its filtering options.
    """
    register_cls = True
    is_custom_base_cls = False

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
        Main function of the operator. Import the selected file.
        It also generates the preview object, updates temporary data and 'dynamic' scene settings.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        settings = context.scene.tbb.settings.telemac
        tmp_data = settings.tmp_data

        # Read the file and update temporary data
        try:
            tmp_data.update(self.filepath)
        except Exception as error:
            print("ERROR::TBB_OT_TelemacImportFile: " + str(error))
            self.report({'ERROR'}, "An error occurred during import")
            return {'FINISHED'}

        settings.file_path = self.filepath

        # Update properties values
        update_scene_settings_dynamic_props(settings, tmp_data)

        try:
            objects = generate_preview_objects(context)

            # Reset preview object dimensions
            settings.preview_obj_dimensions = get_object_dimensions_from_mesh(objects[0])

        except Exception as error:
            print("ERROR::TBB_OT_TelemacImportFile: " + str(error))
            self.report({'ERROR'}, "Something went wrong building the mesh")
            return {'FINISHED'}

        self.report({'INFO'}, "File successfully imported")
        print("Import::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")

        return {'FINISHED'}
