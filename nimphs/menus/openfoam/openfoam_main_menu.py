# <pep8 compliant>
from bpy.types import Menu, Context


class NIMPHS_MT_OpenfoamMainMenu(Menu):
    """Main menu for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "NIMPHS_MT_OpenfoamMainMenu"
    bl_label = "OpenFOAM"

    def draw(self, _context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            _context (Context): context
        """

        self.layout.menu("NIMPHS_MT_OpenfoamCreateSequenceMenu")
        self.layout.menu("NIMPHS_MT_OpenfoamPointDataMenu")
