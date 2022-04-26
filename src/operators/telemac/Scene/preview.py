# <pep8 compliant>
import bpy
from bpy.types import Operator, Context

import time

from ..utils import generate_object, generate_vertex_colors, generate_preview_material


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
        prw_time_point = settings.get("preview_time_point", 0)
        start = time.time()

        try:
            if settings.normalize_preview_obj:
                rescale = 'NORMALIZE'
            else:
                rescale = 'RESET'

            list_point_data = tmp_data.variables_info["names"]

            if not tmp_data.is_3d:
                obj_bottom = generate_object(tmp_data, context, settings, mesh_is_3d=False,
                                             rescale=rescale, time_point=prw_time_point, type='BOTTOM')
                obj_water_depth = generate_object(tmp_data, context, settings, mesh_is_3d=False,
                                                  rescale=rescale, time_point=prw_time_point, type='WATER_DEPTH')

                generate_vertex_colors(tmp_data, obj_bottom.data, list_point_data, prw_time_point)
                generate_vertex_colors(tmp_data, obj_water_depth.data, list_point_data, prw_time_point)
                var_name = tmp_data.variables_info["names"][int(settings.preview_point_data)]
                generate_preview_material(obj_bottom, var_name)
                generate_preview_material(obj_water_depth, var_name)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({"ERROR"}, "An error occurred during preview")
            return {"FINISHED"}

        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
