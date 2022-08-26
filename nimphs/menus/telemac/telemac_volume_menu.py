# <pep8 compliant>
from bpy.types import Menu, Context


class NIMPHS_MT_TelemacVolumeMenu(Menu):
    """Main menu for TELEMAC > Volume."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "NIMPHS_MT_TelemacVolumeMenu"
    bl_label = "Volume"

    def draw(self, _context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            _context (Context): context
        """

        self.layout.operator("nimphs.telemac_generate_volume_sequence", text="Generate volume sequence")
        self.layout.operator("nimphs.set_volume_origin", text="Set volume origin")
