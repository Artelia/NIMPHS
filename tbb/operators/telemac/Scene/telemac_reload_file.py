# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.telemac.file_data import TBB_TelemacFileData


class TBB_OT_TelemacReloadFile(Operator):
    """Operator to reload file data of the selected TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_telemac_file"
    bl_label = "Reload"
    bl_description = "Reload file data of the selected TELEMAC object"

    def execute(self, context: Context) -> set:
        """
        Reload file data of the selected TELEMAC object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        obj = get_selected_object(context)

        # Make sure the object still have an identifier
        if obj.tbb.uid == "":
            obj.tbb.uid = str(time.time())

        # Update file data
        context.scene.tbb.file_data[obj.tbb.uid] = TBB_TelemacFileData(obj.tbb.settings.file_path, False)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
