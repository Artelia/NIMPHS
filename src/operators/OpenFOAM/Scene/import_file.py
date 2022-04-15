# <pep8 compliant>
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from ..utils import load_openopenfoam_file, update_properties_values, generate_preview_object, generate_mesh


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
        success, file_reader = load_openopenfoam_file(self.filepath)

        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Update properties values
        update_properties_values(context, file_reader)
        time_point = settings["preview_time_point"]

        # Update temp data
        context.scene.tbb_openfoam_tmp_data.update(file_reader, time_point)

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while for large meshes.
        try:
            vertices, faces, preview_mesh = generate_mesh(file_reader, time_point)
            blender_mesh, obj = generate_preview_object(vertices, faces, context)
        except Exception as error:
            print("ERROR::TBB_OT_OpenFOAMImportFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}
