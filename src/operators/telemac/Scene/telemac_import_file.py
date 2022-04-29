# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, Context
from bpy.props import StringProperty

import time

from ..utils import generate_object, get_object_dimensions_from_mesh
from ...utils import get_collection, update_scene_settings_dynamic_props


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
        Main function of the operator. Import the selected file.
        It also generates the preview object, updates temporary data and 'dynamic' scene settings.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb_telemac_settings
        tmp_data = context.scene.tbb_telemac_tmp_data
        collection = get_collection("TBB_TELEMAC", context)
        prw_time_point = 0
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
        update_scene_settings_dynamic_props(settings, tmp_data)

        try:
            if not tmp_data.is_3d:
                for obj_type in ['BOTTOM', 'WATER_DEPTH']:
                    obj = generate_object(tmp_data, mesh_is_3d=False, time_point=prw_time_point, type=obj_type)
                    # Reset the scale without applying it
                    obj.scale = [1.0] * 3
                    # Add this new object to the collection
                    if collection.name not in [col.name for col in obj.users_collection]:
                        collection.objects.link(obj)
            else:
                # Create a custom collection for 3D previews
                collection_3d = get_collection("TBB_TELEMAC_3D", context, link_to_scene=False)
                if collection_3d.name not in [col.name for col in collection.children]:
                    collection.children.link(collection_3d)

                for plane_id in range(tmp_data.nb_planes - 1, -1, -1):
                    name = "TBB_TELEMAC_preview_plane_" + str(plane_id)
                    obj = generate_object(tmp_data, mesh_is_3d=True, offset=plane_id,
                                          time_point=prw_time_point, name=name)
                    # Reset the scale without applying it
                    obj.scale = [1.0] * 3

                    # Add this new object to the collection
                    if collection_3d.name not in [col.name for col in obj.users_collection]:
                        collection_3d.objects.link(obj)

            # Reset some preview settings
            settings.preview_obj_dimensions = get_object_dimensions_from_mesh(obj)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacImportFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        print("Import::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}
