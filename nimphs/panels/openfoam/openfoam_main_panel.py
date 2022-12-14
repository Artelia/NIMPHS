# <pep8 compliant>
from bpy.types import Context
from nimphs.panels.openfoam.utils import draw_clip_settings

from nimphs.panels.shared.module_panel import NIMPHS_ModulePanel


class NIMPHS_PT_OpenfoamMainPanel(NIMPHS_ModulePanel):
    """Main panel of the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "OpenFOAM"
    bl_idname = "NIMPHS_PT_OpenfoamMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenFOAM"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        enable_rows, file_data_is_ok, obj = super().draw(context, 'OpenFOAM')

        if obj is not None and file_data_is_ok:
            import_settings = obj.nimphs.settings.openfoam.import_settings

            box = self.layout.box()
            row = box.row()
            row.label(text="Import settings")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "decompose_polyhedra", text="Decompose polyhedra")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "skip_zero_time", text="Skip zero time")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "triangulate", text="Triangulate")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "case_type", text="Case")

            # Clip settings
            file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)
            enable_clip = file_data.time_point == obj.nimphs.settings.preview_time_point

            draw_clip_settings(self.layout, obj.nimphs.settings.openfoam.clip, enable=enable_clip)

            # Preview settings
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
            row.operator("nimphs.openfoam_preview", text="Preview", icon='HIDE_OFF')

            if not enable_clip:
                row = self.layout.box().row()
                row.label(text="No data. Hit 'preview'.", icon='ERROR')

        elif obj is None or (not obj.nimphs.is_streaming_sequence and file_data_is_ok):
            row = self.layout.row()
            row.label(text="Select an OpenFOAM object", icon='INFO')
