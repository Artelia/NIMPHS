# <pep8 compliant>
from bpy.types import Operator, Context

import time
import logging
log = logging.getLogger(__name__)

from tbb.operators.telemac.utils import generate_base_objects, generate_preview_objects
from tbb.panels.utils import get_selected_object


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

        obj = get_selected_object(context)
        collection = context.scene.collection
        tmp_data = context.scene.tbb.tmp_data[obj.tbb.uid]
        prw_time_point = obj.tbb.settings.preview_time_point

        try:
            children = generate_base_objects(tmp_data, prw_time_point, obj.name)

            for child in children:
                # Check if not already in collection
                if collection.name not in [col.name for col in child.users_collection]:
                    collection.objects.link(obj)

        except Exception:
            log.error("An error occurred during preview", exc_info=1)
            self.report({'ERROR'}, "An error occurred during preview")
            return {'FINISHED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Mesh successfully built: checkout the viewport.")

        return {'FINISHED'}
