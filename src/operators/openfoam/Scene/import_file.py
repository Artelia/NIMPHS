# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, Context
from bpy.props import StringProperty

import time

from ..utils import load_openfoam_file, update_settings_dynamic_props, generate_mesh
from ...utils import generate_object_from_data
from ....properties.openfoam.utils import encode_value_ranges, encode_scalar_names


class TBB_OT_OpenfoamImportFile(Operator, ImportHelper):
    """
    Import an OpenFOAM file. This operator manages the file browser and its filtering options.
    """

    bl_idname = "tbb.import_openfoam_file"
    bl_label = "Import"
    bl_description = "Import an OpenFOAM file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.foam",  # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Import the selected file. It also generates the preview object.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb_openfoam_settings
        tmp_data = context.scene.tbb_openfoam_tmp_data
        start = time.time()
        success, file_reader = load_openfoam_file(self.filepath)

        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Update properties values
        update_settings_dynamic_props(context, file_reader)
        time_point = settings["preview_time_point"]

        # Update temp data
        tmp_data.update(file_reader, time_point)
        settings.clip.scalar.value_ranges = encode_value_ranges(tmp_data.mesh)
        settings.clip.scalar.list = encode_scalar_names(tmp_data.mesh)

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while for large meshes.
        try:
            vertices, faces, preview_mesh = generate_mesh(file_reader, time_point)
            blender_mesh, obj = generate_object_from_data(vertices, faces, context, "TBB_OpenFOAM_preview")
        except Exception as error:
            print("ERROR::TBB_OT_OpenfoamImportFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        print("Import::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}
