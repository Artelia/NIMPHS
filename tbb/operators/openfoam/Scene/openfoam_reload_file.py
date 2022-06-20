# <pep8 compliant>
from bpy.types import Operator, Context

import time
import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.operators.openfoam.utils import load_openfoam_file
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData


class TBB_OT_OpenfoamReloadFile(Operator):
    """Reload the selected file."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_openfoam_file"
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
        io_settings = obj.tbb.settings.openfoam.import_settings
        success, file_reader = load_openfoam_file(obj.tbb.settings.file_path, io_settings.case_type,
                                                  io_settings.decompose_polyhedra)

        if not success:
            self.report({'WARNING'}, "The chosen file can't be read")
            return {'FINISHED'}

        # Make sure the object still have an identifier
        if obj.tbb.uid == "":
            obj.tbb.uid = str(time.time())

        # Update temporary data
        context.scene.tbb.tmp_data[obj.tbb.uid] = TBB_OpenfoamFileData(file_reader, io_settings)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successful")

        return {'FINISHED'}
