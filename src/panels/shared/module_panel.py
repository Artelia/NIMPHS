# <pep8 compliant>
from bpy.types import Panel, Context, Object

from ..utils import get_selected_object
from ...properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from ...properties.telemac.temporary_data import TBB_TelemacTemporaryData
from ...properties.shared.scene_settings import TBB_ModuleSceneSettings


class TBB_ModulePanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC modules.
    Specific settings are added in the classes which derive from this one.
    """

    def draw(self, settings: TBB_ModuleSceneSettings, tmp_data: TBB_OpenfoamTemporaryData |
             TBB_TelemacTemporaryData, context: Context) -> tuple[bool, Object | None]:
        """
        Layout of the panel.

        :param settings: scene settings
        :type settings: TBB_SceneSettings
        :param tmp_data: temporary data
        :type tmp_data: TBB_OpenfoamTemporaryData | TBB_TelemacTemporaryData
        :type context: Context
        :return: enable rows, selected object
        :rtype: tuple[bool, Object | None]
        """

        layout = self.layout
        module = tmp_data.module_name
        obj = get_selected_object(context)

        if obj is not None:
            if module == 'OpenFOAM':
                sequence_settings = obj.tbb_openfoam_sequence
            if module == 'TELEMAC':
                sequence_settings = obj.tbb_telemac_sequence
        else:
            sequence_settings = None

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb_create_sequence_is_running

        row = layout.row()
        row.label(text="Import")

        # Import section
        row = layout.row()
        if settings.file_path != "":
            box = row.box()
            box.label(text="File: " + settings.file_path)
            row = layout.row()
            row.enabled = enable_rows
            row.operator("tbb.import_" + module.lower() + "_file", text="Import", icon="IMPORT")
            row.operator("tbb.reload_" + module.lower() + "_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.enabled = enable_rows
            row.operator("tbb.import_" + module.lower() + "_file", text="Import " + module + " file", icon="IMPORT")

        if sequence_settings is None or not sequence_settings.is_streaming_sequence:

            if tmp_data.is_ok():
                # Preview section
                row = layout.row()
                row.enabled = enable_rows
                row.label(text="Preview")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, '["preview_time_point"]', text="Time step")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, "preview_point_data", text="Points")

            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            elif settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")

        else:
            row = layout.row()
            row.label(text="Edit settings of this sequence in the object properties panel", icon="INFO")

            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            if not tmp_data.is_ok() and settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")

        return enable_rows, obj
