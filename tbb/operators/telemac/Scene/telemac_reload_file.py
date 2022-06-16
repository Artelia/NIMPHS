# <pep8 compliant>
from bpy.types import Operator, Context

import time
import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData


class TBB_OT_TelemacReloadFile(Operator):
    """Reload the selected file."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_telemac_file"
    bl_label = "Reload"
    bl_description = "Reload the selected file"

    def execute(self, context: Context) -> set:
        """
        Reload the selected file.

        It updates temporary data and 'dynamic' scene settings.

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

        # Update temporary data
        context.scene.tbb.tmp_data[obj.tbb.uid] = TBB_TelemacTemporaryData(obj.tbb.settings.file_path, False)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
