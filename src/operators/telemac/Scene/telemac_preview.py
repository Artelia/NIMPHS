# <pep8 compliant>
from bpy.types import Operator, Context

import time

from ..utils import normalize_objects, generate_preview_objects, get_collection


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

        start = time.time()

        settings = context.scene.tbb.settings.telemac

        try:
            objects = generate_preview_objects(context, time_point=settings["preview_time_point"])

            if settings.normalize_preview_obj:
                normalize_objects(objects, settings.preview_obj_dimensions)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({"ERROR"}, "An error occurred during preview")
            return {"FINISHED"}

        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")
        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")

        return {"FINISHED"}
