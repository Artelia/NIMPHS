# <pep8 compliant>
from bpy.types import Menu, Context


class TBB_MT_TelemacMainMenu(Menu):
    """Main menu for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "TBB_MT_TelemacMainMenu"
    bl_label = "TELEMAC"

    def draw(self, _context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            _context (Context): context
        """

        self.layout.menu("TBB_MT_TelemacCreateSequenceMenu")
        self.layout.menu("TBB_MT_TelemacPointDataMenu")
