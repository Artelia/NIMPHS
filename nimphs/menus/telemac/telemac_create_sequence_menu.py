# <pep8 compliant>
from bpy.types import Menu, Context


class NIMPHS_MT_TelemacCreateSequenceMenu(Menu):
    """Main menu for the TELEMAC > Create sequence."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "NIMPHS_MT_TelemacCreateSequenceMenu"
    bl_label = "Create sequence"

    def draw(self, _context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            _context (Context): context
        """

        self.layout.operator("nimphs.telemac_create_mesh_sequence", text="Mesh sequence")
        op = self.layout.operator("nimphs.telemac_create_streaming_sequence", text="Streaming sequence")
        op.module = 'TELEMAC'
