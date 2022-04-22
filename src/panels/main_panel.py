# <pep8 compliant>
from bpy.types import Panel, Context


class TBB_PT_MainPanel(Panel):
    """
    Main panel of the Toolsbox blender add-on.
    """

    bl_label = "Toolsbox"
    bl_idname = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolsbox blender"

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """
