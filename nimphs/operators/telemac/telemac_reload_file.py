# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from nimphs.panels.utils import get_selected_object
from nimphs.properties.utils.point_data import PointDataManager
from nimphs.properties.telemac.file_data import TelemacFileData


class NIMPHS_OT_TelemacReloadFile(Operator):
    """Operator to reload file data of the selected TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.reload_telemac_file"
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

        # Generated new file data
        try:
            file_data = TelemacFileData(obj.nimphs.settings.file_path)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Make sure the object still have an identifier
        if obj.nimphs.uid == "":
            obj.nimphs.uid = str(time.time())

        # Load saved information
        context.scene.nimphs.file_data[obj.nimphs.uid] = file_data
        if obj.nimphs.settings.point_data.save != "":
            context.scene.nimphs.file_data[obj.nimphs.uid].vars = PointDataManager(obj.nimphs.settings.point_data.save)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
