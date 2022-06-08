# <pep8 compliant>
from bpy.props import StringProperty
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper

import time

from tbb.operators.openfoam.utils import load_openfoam_file, generate_mesh_data
from tbb.properties.openfoam.utils import encode_value_ranges, encode_scalar_names
from tbb.operators.utils import generate_object_from_data, get_collection, update_scene_settings_dynamic_props


class TBB_OT_OpenfoamImportFile(Operator, ImportHelper):
    """
    Import an OpenFOAM file. This operator manages the file browser and its filtering options.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.import_openfoam_file"
    bl_label = "Import"
    bl_description = "Import an OpenFOAM file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.foam",  # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
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

        settings = context.scene.tbb.settings.openfoam
        tmp_data = settings.tmp_data
        collection = get_collection("TBB_OpenFOAM", context)

        start = time.time()
        success, file_reader = load_openfoam_file(self.filepath, settings.case_type, settings.decompose_polyhedra)

        if not success:
            self.report({'ERROR'}, "The chosen file does not exist")
            return {'FINISHED'}

        settings.file_path = self.filepath

        # Update temp data
        tmp_data.update(file_reader, 0)

        # Update properties values
        update_scene_settings_dynamic_props(settings, tmp_data)
        settings.clip.scalar.value_ranges = encode_value_ranges(tmp_data.mesh)
        settings.clip.scalar.list = encode_scalar_names(tmp_data.mesh)

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while for large meshes.
        try:
            vertices, faces, preview_mesh = generate_mesh_data(file_reader, 0, triangulate=settings.triangulate)
            obj = generate_object_from_data(vertices, faces, "TBB_OpenFOAM_preview")
            if collection.name not in [col.name for col in obj.users_collection]:
                collection.objects.link(obj)
        except Exception as error:
            print("ERROR::TBB_OT_OpenfoamImportFile: " + str(error))
            self.report({'ERROR'}, "Something went wrong building the mesh")
            return {'FINISHED'}

        print("Import::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "File successfully imported")

        return {'FINISHED'}
