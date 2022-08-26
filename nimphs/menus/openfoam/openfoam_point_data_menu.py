# <pep8 compliant>
from bpy.types import Menu, Context

from nimphs.panels.utils import get_selected_object


class NIMPHS_MT_OpenfoamPointDataMenu(Menu):
    """Main menu for OpenFOAM > Point data."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "NIMPHS_MT_OpenfoamPointDataMenu"
    bl_label = "Point data"

    def draw(self, context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)

        row = self.layout.row()
        row.enabled = obj.nimphs.module == 'OpenFOAM' if obj is not None else False
        row.operator("nimphs.compute_ranges_point_data_values", text="Compute ranges")
