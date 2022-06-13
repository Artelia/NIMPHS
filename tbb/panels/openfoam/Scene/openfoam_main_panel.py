# <pep8 compliant>
from bpy.types import Context
from tbb.operators.utils import get_temporary_data

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

        enable_rows, obj = super().draw(context)

        if obj is not None:
            import_settings = obj.tbb.settings.openfoam.import_settings

            layout = self.layout

            layout.separator()

            row = layout.row()
            row.label(text="Import settings")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(import_settings, "decompose_polyhedra", text="Decompose polyhedra")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(import_settings, "triangulate", text="Triangulate")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(import_settings, "case_type", text="Case")

            layout.separator()

            row = layout.row()
            row.label(text="Preview")

            row = layout.row()
            row.enabled = enable_rows
            row.prop(obj.tbb.settings.openfoam, "preview_point_data", text="Point")

            row = layout.row()
            row.enabled = enable_rows
            row.prop(obj.tbb.settings.openfoam, "preview_time_point", text="Time point")

            row = layout.row()
            row.enabled = enable_rows
            row.operator("tbb.openfoam_preview", text="Preview", icon='HIDE_OFF')
