# <pep8 compliant>
from bpy.types import AddonPreferences, Context
from bpy.props import PointerProperty

from tbb.properties.preferences import TBB_Preferences


class TBB_Preferences(AddonPreferences):
    """UI panel to manage addon's preferences."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = __package__.removesuffix(".panels")

    #: bpy.props.PointerProperty: Preferences of the addon.
    # Access through `context.preferences.addons['tbb'].preferences.settings`.
    settings: PointerProperty(type=TBB_Preferences)

    def draw(self, context: Context) -> None:
        """
        UI layout of this panel.

        Args:
            context (Context): context
        """

        # Files preferences
        box = self.layout.box()

        row = box.row()
        row.label(text="Files")

        row = box.row()
        row.prop(self.settings, "openfoam_extensions", text="OpenFOAM")

        row = box.row()
        row.prop(self.settings, "telemac_extensions", text="TELEMAC")

        # System preferences
        box = self.layout.box()

        row = box.row()
        row.label(text="System")

        row = box.row()
        row.prop(self.settings, "log_level", text="Log")
