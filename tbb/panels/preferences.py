# <pep8 compliant>
from bpy.types import AddonPreferences, Context
from bpy.props import PointerProperty

from tbb.properties.preferences import TBB_Preferences


class TBB_Preferences(AddonPreferences):
    """UI panel to manage addon's preferences."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = __package__.removesuffix(".panels")

    preferences: PointerProperty(type=TBB_Preferences)

    def draw(self, context: Context) -> None:
        """
        UI layout of this panel.

        Args:
            context (Context): context
        """

        layout = self.layout

        row = layout.row()
        row.prop(self.preferences, "log_level", text="Log")
