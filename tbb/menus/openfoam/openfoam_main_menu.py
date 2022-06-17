# <pep8 compliant>
from bpy.types import Menu, Context


class TBB_MT_OpenfoamMainMenu(Menu):
    """Main menu for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "TBB_MT_OpenfoamMainMenu"
    bl_label = "OpenFOAM"

    def draw(self, context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            context (Context): context
        """

        self.layout.menu("TBB_MT_OpenfoamCreateSequenceMenu")
