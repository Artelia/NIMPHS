# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

import time

from ..utils import load_openopenfoam_file, update_settings_dynamic_props, generate_preview_object, generate_mesh
from ....properties.OpenFOAM.utils import encode_value_ranges, encode_scalar_names


class TBB_OT_OpenFOAMImportFile(Operator, ImportHelper):
    bl_idname = "tbb.import_openfoam_file"
    bl_label = "Import"
    bl_description = "Import an OpenFoam file"

    filter_glob: StringProperty(
        default="*.foam",  # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        settings = context.scene.tbb_openfoam_settings
        tmp_data = context.scene.tbb_openfoam_tmp_data
        start = time.time()
        success, file_reader = load_openopenfoam_file(self.filepath)

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
            blender_mesh, obj = generate_preview_object(vertices, faces, context)
        except Exception as error:
            print("ERROR::TBB_OT_OpenFOAMImportFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        print("Import::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}
