# <pep8 compliant>
from bpy.types import Menu, Context


class TBB_MT_TelemacMainMenu(Menu):
    """Main menu for the TELEMAC module."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "TBB_MT_TelemacMainMenu"
    bl_label = "TELEMAC"

    def draw(self, context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            context (Context): context
        """

        layout = self.layout

        layout.menu("TBB_MT_TelemacCreateSequenceMenu")
