# <pep8 compliant>
from bpy.types import Operator, Context

import time

from tbb.properties.openfoam.utils import encode_value_ranges, encode_scalar_names
from tbb.operators.utils import generate_object_from_data, get_collection, generate_vertex_colors
from tbb.operators.openfoam.utils import (
    generate_mesh_data,
    prepare_openfoam_point_data,
    generate_preview_material,
    load_openfoam_file)


class TBB_OT_OpenfoamPreview(Operator):
    """
    Preview the mesh using the loaded file and selected parameters.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Preview the mesh.
        It also updates temporary data with this new preview.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        settings = context.scene.tbb.settings.openfoam
        tmp_data = settings.tmp_data
        prw_time_point = settings["preview_time_point"]
        collection = get_collection("TBB_OpenFOAM", context)
        clip = settings.clip

        if settings.file_path == "":
            self.report({'ERROR'}, "Please import a file first.")
            return {'FINISHED'}

        if clip.type != "" and clip.scalar.name == "":
            self.report({'ERROR'}, "Select a scalar to clip on. You may need to reload the file if none are shown")
            return {'FINISHED'}

        start = time.time()
        # TODO: changing time point does not work if we do not load the file
        # again... We would like to use the file_reader from tbb.settings.openfoam.tmp_data.
        success, file_reader = load_openfoam_file(settings.file_path, settings.case_type, settings.decompose_polyhedra)
        if not success:
            self.report({'ERROR'}, "The chosen file does not exist.")
            return {'FINISHED'}

        # Read data at the chosen time point
        try:
            file_reader.set_active_time_point(prw_time_point)
        except ValueError as error:
            print("ERROR::TBB_OT_OpenfoamPreview: " + str(error))
            self.report({'ERROR'}, "The selected time point is not defined (" + str(prw_time_point) + ").")
            return {'FINISHED'}

        data = file_reader.read()
        raw_mesh = data["internalMesh"]
        clip.scalar.value_ranges = encode_value_ranges(raw_mesh)
        clip.scalar.list = encode_scalar_names(raw_mesh)

        try:
            vertices, faces, mesh = generate_mesh_data(
                file_reader, prw_time_point, triangulate=settings.triangulate, clip=clip, mesh=raw_mesh)
        except Exception as error:
            print("ERROR::TBB_OT_OpenfoamPreview: " + str(error))
            # Update temporary data, please read the comment below.
            tmp_data.update(file_reader, prw_time_point, data, raw_mesh)
            self.report({'ERROR'}, "Something went wrong building the mesh")
            return {'FINISHED'}

        # Update temporary data. We do not update it just after the reading of the file. Here is why.
        # This line will update the list of available scalars. If the chosen scalar is not available at
        # the selected time point, the program will automatically choose another scalar due to the update function
        # of the enum property. This is surely not what the user was expecting.
        tmp_data.update(file_reader, prw_time_point, data, raw_mesh)

        try:
            obj = generate_object_from_data(vertices, faces, "TBB_OpenFOAM_preview")
            blender_mesh = obj.data
            if collection.name not in [col.name for col in obj.users_collection]:
                collection.objects.link(obj)
        except Exception as error:
            print("ERROR::TBB_OT_OpenfoamPreview: " + str(error))
            self.report({'ERROR'}, "Something went generating the object")
            return {'FINISHED'}

        res = prepare_openfoam_point_data(mesh, blender_mesh, [settings.preview_point_data], prw_time_point)
        if len(res[0]) > 0:
            generate_vertex_colors(blender_mesh, *res)
            generate_preview_material(obj, res[0][0]["name"] if len(res[0]) > 0 else 'None')

        print("Preview::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Mesh successfully built: checkout the viewport.")

        return {'FINISHED'}
