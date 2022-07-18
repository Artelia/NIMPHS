# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData
from tbb.properties.utils.point_data import PointDataManager


class TBB_OT_OpenfoamReloadFile(Operator):
    """Operator to reload file data of the selected OpenFOAM object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload file data of the selected OpenFOAM object"

    def execute(self, context: Context) -> set:
        """
        Reload file data of the selected OpenFOAM object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        obj = get_selected_object(context)
        io_settings = obj.tbb.settings.openfoam.import_settings

        # Generate new file data
        try:
            file_data = TBB_OpenfoamFileData(obj.tbb.settings.file_path, io_settings)
        except BaseException:
            self.report({'WARNING'}, "An error occurred reading the file")
            return {'CANCELLED'}

        # Make sure the object still have an identifier
        if obj.tbb.uid == "":
            obj.tbb.uid = str(time.time())

        # Load saved information
        context.scene.tbb.file_data[obj.tbb.uid] = file_data
        if obj.tbb.settings.point_data.save != "":
            context.scene.tbb.file_data[obj.tbb.uid].vars = PointDataManager(obj.tbb.settings.point_data.save)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
