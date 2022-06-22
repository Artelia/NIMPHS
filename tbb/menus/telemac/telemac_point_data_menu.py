# <pep8 compliant>
from bpy.types import Menu, Context


class TBB_MT_TelemacPointDataMenu(Menu):
    """Main menu for TELEMAC > Point data."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "TBB_MT_TelemacPointDataMenu"
    bl_label = "Point data"

    def draw(self, _context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            _context (Context): context
        """

        self.layout.operator("tbb.compute_ranges_point_data_values", text="Compute ranges")
