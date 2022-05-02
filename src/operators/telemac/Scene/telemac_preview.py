# <pep8 compliant>
from bpy.types import Operator, Context

import time

from ..utils import generate_mesh, generate_vertex_colors, generate_preview_material, normalize_objects
from ...utils import get_collection, generate_object_from_data


class TBB_OT_TelemacPreview(Operator):
    """
    Preview the mesh using the loaded file and selected parameters.
    """

    bl_idname = "tbb.telemac_preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Preview the mesh.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb.settings.telemac
        tmp_data = settings.tmp_data
        collection = get_collection("TBB_TELEMAC", context)
        prw_time_point = settings.get("preview_time_point", 0)
        start = time.time()

        # Prepare list of point data to preview
        prw_var_id = int(settings.preview_point_data)
        import_point_data = prw_var_id >= 0
        if import_point_data:
            vertex_colors_var_name = tmp_data.vars_info["names"][prw_var_id]
            list_point_data = [vertex_colors_var_name]
            # Generate vertex colors for all the variables
            # list_point_data = tmp_data.vars_info["names"]

        try:
            objs_to_normalize = []
            if not tmp_data.is_3d:
                for obj_type in ['BOTTOM', 'WATER_DEPTH']:
                    name = "TBB_TELEMAC_preview" + "_" + obj_type.lower()
                    vertices = generate_mesh(tmp_data, mesh_is_3d=False, time_point=prw_time_point, type=obj_type)
                    obj = generate_object_from_data(vertices, tmp_data.faces, name=name)
                    if import_point_data:
                        generate_vertex_colors(tmp_data, obj.data, list_point_data, prw_time_point)
                        generate_preview_material(obj, vertex_colors_var_name)
                    # Reset the scale without applying it
                    obj.scale = [1.0] * 3

                    objs_to_normalize.append(obj)

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
                    vertices = generate_mesh(tmp_data, mesh_is_3d=True, offset=plane_id, time_point=prw_time_point)
                    obj = generate_object_from_data(vertices, tmp_data.faces, name=name)
                    if import_point_data:
                        generate_vertex_colors(tmp_data, obj.data, list_point_data, prw_time_point,
                                               mesh_is_3d=True, offset=plane_id)
                        generate_preview_material(obj, vertex_colors_var_name)
                    # Reset the scale without applying it
                    obj.scale = [1.0] * 3

                    objs_to_normalize.append(obj)

                    # Add this new object to the collection
                    if collection_3d.name not in [col.name for col in obj.users_collection]:
                        collection_3d.objects.link(obj)

            if settings.normalize_preview_obj:
                normalize_objects(objs_to_normalize, settings.preview_obj_dimensions)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({"ERROR"}, "An error occurred during preview")
            return {"FINISHED"}

        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
