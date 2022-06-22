# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.operators.telemac.utils import generate_base_objects


class TBB_OT_TelemacPreview(Operator):
    """Operator to generate a preview of a TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_preview"
    bl_label = "Preview"
    bl_description = "Preview the selected file"

    def execute(self, context: Context) -> set:
        """
        Generate a preview of the selected object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        obj = get_selected_object(context)
        collection = context.scene.collection
        file_data = context.scene.tbb.file_data.get(obj.tbb.uid, None)
        time_point = obj.tbb.settings.preview_time_point
        point_data = obj.tbb.settings.preview_point_data

        try:
            file_data.update_data(time_point)
            children = generate_base_objects(file_data, obj.name, point_data)

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
