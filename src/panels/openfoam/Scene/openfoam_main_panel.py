# <pep8 compliant>
from bpy.types import Context

from ...module_panel import ModulePanel


class TBB_PT_OpenfoamMainPanel(ModulePanel):
    """
    Main panel of the OpenFOAM module. This is the 'parent' panel.
    """

    bl_label = "OpenFOAM"
    bl_idname = "TBB_PT_OpenfoamMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenFOAM"

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        settings = context.scene.tbb_openfoam_settings
        tmp_data = context.scene.tbb_openfoam_tmp_data
        enable_rows, obj = ModulePanel.draw(self, settings, tmp_data, context)

        layout = self.layout
        if obj is not None:
            sequence_settings = obj.tbb_openfoam_sequence
        else:
            sequence_settings = None

        if sequence_settings is None or not sequence_settings.is_streaming_sequence:

            if tmp_data.is_ok():
                row = layout.row()
                row.enabled = enable_rows
                row.operator("tbb.openfoam_preview", text="Preview", icon="HIDE_OFF")
