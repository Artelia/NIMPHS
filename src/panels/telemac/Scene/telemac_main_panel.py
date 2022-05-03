# <pep8 compliant>
from bpy.types import Context

from ...shared.module_panel import TBB_ModulePanel


class TBB_PT_TelemacMainPanel(TBB_ModulePanel):
    """
    Main panel of the TELEMAC module. This is the 'parent' panel.
    """

    bl_label = "TELEMAC"
    bl_idname = "TBB_PT_TelemacMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TELEMAC"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls 'super().draw(...)'.

        :type context: Context
        """

        settings = context.scene.tbb.settings.telemac
        tmp_data = settings.tmp_data
        enable_rows, obj = super().draw(settings, tmp_data, context)

        layout = self.layout
        if obj is not None:
            sequence_settings = obj.tbb.settings.telemac.streaming_sequence
        else:
            sequence_settings = None

        if sequence_settings is None or not obj.tbb.is_streaming_sequence:

            if tmp_data.is_ok():
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, "normalize_preview_obj", text="Normalize")
                row = layout.row()
                row.enabled = enable_rows
                row.operator("tbb.telemac_preview", text="Preview", icon="HIDE_OFF")
