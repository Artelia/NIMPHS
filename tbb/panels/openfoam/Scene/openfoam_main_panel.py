# <pep8 compliant>
from bpy.types import Context
from tbb.panels.openfoam.utils import draw_clip_settings

from tbb.panels.shared.module_panel import TBB_ModulePanel


class TBB_PT_OpenfoamMainPanel(TBB_ModulePanel):
    """Main panel of the OpenFOAM module. This is the 'parent' panel."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "OpenFOAM"
    bl_idname = "TBB_PT_OpenfoamMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenFOAM"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls parent draw function.

        Args:
            context (Context): context
        """

        enable_rows, tmp_data_is_ok, obj = super().draw(context)

        if obj is not None and tmp_data_is_ok:
            import_settings = obj.tbb.settings.openfoam.import_settings

            box = self.layout.box()
            row = box.row()
            row.label(text="Import settings")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "decompose_polyhedra", text="Decompose polyhedra")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "triangulate", text="Triangulate")
            row = box.row()
            row.enabled = enable_rows
            row.prop(import_settings, "case_type", text="Case")

            # Clip settings
            tmp_data = context.scene.tbb.tmp_data[obj.tbb.uid]
            enable_clip = tmp_data.time_point == obj.tbb.settings.openfoam.preview_time_point

            draw_clip_settings(self.layout, obj.tbb.settings.openfoam.clip, enable=enable_clip)

            box = self.layout.box()
            row = box.row()
            row.label(text="Preview")

            row = box.row()
            row.enabled = enable_rows
            row.prop(obj.tbb.settings.openfoam, "preview_point_data", text="Point")

            row = box.row()
            row.enabled = enable_rows
            row.prop(obj.tbb.settings.openfoam, "preview_time_point", text="Time point")

            row = box.row()
            row.enabled = enable_rows
            row.operator("tbb.openfoam_preview", text="Preview", icon='HIDE_OFF')

            if not enable_clip:
                row = self.layout.box().row()
                row.label(text="No data. Hit 'preview'.", icon='ERROR')

        elif obj is None:
            row = self.layout.row()
            row.label(text="Select an OpenFOAM object", icon='INFO')
