# <pep8 compliant>
from bpy.types import Context

from tbb.panels.shared.module_panel import TBB_ModulePanel


class TBB_PT_TelemacMainPanel(TBB_ModulePanel):
    """Main panel of the TELEMAC module. This is the 'parent' panel."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC"
    bl_idname = "TBB_PT_TelemacMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TELEMAC"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls parent draw function.

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
            row.prop(obj.tbb.settings, "preview_point_data", text="Point")

            row = box.row()
            row.enabled = enable_rows
            row.prop(obj.tbb.settings, "preview_time_point", text="Time point")

            row = box.row()
            row.enabled = enable_rows
            row.operator("tbb.telemac_preview", text="Preview", icon='HIDE_OFF')

        elif obj is None or (not obj.tbb.is_streaming_sequence and file_data_is_ok):
            row = self.layout.row()
            row.label(text="Select a TELEMAC object", icon='INFO')
