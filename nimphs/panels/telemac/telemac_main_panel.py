# <pep8 compliant>
from bpy.types import Context

from nimphs.panels.shared.module_panel import NIMPHS_ModulePanel


class NIMPHS_PT_TelemacMainPanel(NIMPHS_ModulePanel):
    """Main panel of the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC"
    bl_idname = "NIMPHS_PT_TelemacMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TELEMAC"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        enable_rows, file_data_is_ok, obj = super().draw(context, 'TELEMAC')

        if obj is not None and file_data_is_ok:
            box = self.layout.box()
            row = box.row()
            row.label(text="Preview")

            row = box.row()
            row.enabled = enable_rows
            row.prop(obj.nimphs.settings, "preview_point_data", text="Point")

            row = box.row()
            row.enabled = enable_rows
            row.prop(obj.nimphs.settings, "preview_time_point", text="Time point")

            row = box.row()
            row.enabled = enable_rows
            row.operator("nimphs.telemac_preview", text="Preview", icon='HIDE_OFF')

        elif obj is None or (not obj.nimphs.is_streaming_sequence and file_data_is_ok):
            row = self.layout.row()
            row.label(text="Select a TELEMAC object", icon='INFO')
