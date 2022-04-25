# <pep8 compliant>
import bpy
from bpy.types import Operator, Context

import time

from ..utils import generate_object, generate_vertex_colors


class TBB_OT_TelemacPreview(Operator):
    """
    Preview the mesh using the loaded file and selected parameters.
    """

    bl_idname = "tbb.telemac_preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

    def execute(self, context: Context) -> set:
        """
        Preview the mesh.

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

            obj = generate_object(tmp_data, context, settings, rescale=rescale, time_point=prw_time_point)
            list_point_data = [tmp_data.file.nomvar[int(settings.preview_point_data)]]
            generate_vertex_colors(tmp_data, obj.data, list_point_data, prw_time_point)
        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({"ERROR"}, "An error occurred during preview")
            return {"FINISHED"}

        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
