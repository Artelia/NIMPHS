# <pep8 compliant>
from bpy.types import Operator, Context

import time

from tbb.operators.telemac.utils import normalize_objects, generate_preview_objects


class TBB_OT_TelemacPreview(Operator):
    """Preview the mesh using the loaded file and selected parameters."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

    def execute(self, context: Context) -> set:
        """
        Preview the mesh.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        settings = context.scene.tbb.settings.telemac

        try:
            objects = generate_preview_objects(context, time_point=settings["preview_time_point"])

            if settings.normalize_preview_obj:
                normalize_objects(objects, settings.preview_obj_dimensions)

        except Exception as error:
            print("ERROR::TBB_OT_TelemacPreview: " + str(error))
            self.report({'ERROR'}, "An error occurred during preview")
            return {'FINISHED'}

        self.report({'INFO'}, "Mesh successfully built: checkout the viewport.")
        print("Preview::TELEMAC: " + "{:.4f}".format(time.time() - start) + "s")

        return {'FINISHED'}
