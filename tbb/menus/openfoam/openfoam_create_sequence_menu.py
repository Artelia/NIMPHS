# <pep8 compliant>
from bpy.types import Menu, Context


class TBB_MT_OpenfoamCreateSequenceMenu(Menu):
    """Main menu for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "TBB_MT_OpenfoamCreateSequenceMenu"
    bl_label = "Create sequence"

    def draw(self, context: Context) -> None:
        """
        UI layout of the menu.

        Args:
            context (Context): context
        """

        self.layout.operator("tbb.openfoam_create_mesh_sequence", text="Mesh sequence")
        op = self.layout.operator("tbb.openfoam_create_streaming_sequence", text="Streaming sequence")
        op.module = 'OpenFOAM'
