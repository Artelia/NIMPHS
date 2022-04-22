# <pep8 compliant>
from bpy.types import Panel, Context


class TBB_PT_TelemacMainPanel(Panel):
    """
    Main panel of the TELEMAC module. This is the 'parent' panel.
    """

    bl_label = "TELEMAC"
    bl_idname = "TBB_PT_TelemacMainPanel"
    bl_parent_id = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """
