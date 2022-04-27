# <pep8 compliant>
from bpy.types import Operator, Context

import time

from ..utils import generate_object, generate_vertex_colors, generate_preview_material, normalize_preview
from ...utils import get_collection


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

        settings = context.scene.tbb_telemac_settings
        tmp_data = context.scene.tbb_telemac_tmp_data
        collection = get_collection("TBB_TELEMAC", context)
        prw_time_point = settings.get("preview_time_point", 0)
        start = time.time()

        list_point_data = tmp_data.variables_info["names"]
        vertex_colors_var_name = tmp_data.variables_info["names"][int(settings.preview_point_data)]

        try:
            if not tmp_data.is_3d:
                for obj_type in ['BOTTOM', 'WATER_DEPTH']:
                    obj = generate_object(tmp_data, context, settings, mesh_is_3d=False,
                                          time_point=prw_time_point, type=obj_type)
                    generate_vertex_colors(tmp_data, obj.data, list_point_data, prw_time_point)
                    generate_preview_material(obj, vertex_colors_var_name)
                    # Reset the scale without applying it
                    obj.scale = [1.0] * 3

                    if collection.name not in [col.name for col in obj.users_collection]:
                        collection.objects.link(obj)

            if settings.normalize_preview_obj:
                normalize_preview(collection, settings.preview_obj_dimensions)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({"ERROR"}, "An error occurred during preview")
            return {"FINISHED"}

        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
