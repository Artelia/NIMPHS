# <pep8 compliant>
from bpy.types import Operator, Context

import time

from src.operators.openfoam.utils import load_openfoam_file
from src.operators.utils import update_scene_settings_dynamic_props
from src.properties.openfoam.utils import encode_value_ranges, encode_scalar_names


class TBB_OT_OpenfoamReloadFile(Operator):
    """
    Reload the selected file.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.reload_openfoam_file"
    bl_label = "Reload"
    bl_description = "Reload the selected file"

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Reload the selected file.
        It updates temporary data and 'dynamic' scene settings.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        settings = context.scene.tbb.settings.openfoam
        tmp_data = settings.tmp_data

        if settings.file_path == "":
            self.report({'ERROR'}, "Please select a file first")
            return {'FINISHED'}

        start = time.time()
        success, file_reader = load_openfoam_file(settings.file_path, settings.case_type, settings.decompose_polyhedra)
        if not success:
            self.report({'ERROR'}, "The choosen file does not exist")
            return {'FINISHED'}

        # Update temp data
        tmp_data.update(file_reader, settings.get("preview_time_point", 0))
        settings.clip.scalar.value_ranges = encode_value_ranges(tmp_data.mesh)
        settings.clip.scalar.list = encode_scalar_names(tmp_data.mesh)
        context.scene.tbb.create_sequence_is_running = False

        # Update properties values
        update_scene_settings_dynamic_props(settings, tmp_data)

        print("Reload::OpenFOAM: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Reload successfull")

        return {'FINISHED'}
