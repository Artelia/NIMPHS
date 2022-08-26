# <pep8 compliant>
from bpy.props import PointerProperty
from bpy.types import AddonPreferences, Context

from nimphs.properties.preferences import NIMPHS_Preferences


class NIMPHS_Preferences(AddonPreferences):
    """UI panel to manage add-on's preferences."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = __package__.removesuffix(".panels")

    #: bpy.props.PointerProperty: Preferences of the addon.
    # Access through `context.preferences.addons['nimphs'].preferences.settings`.
    settings: PointerProperty(type=NIMPHS_Preferences)

    def draw(self, _context: Context) -> None:
        """
        UI layout of this panel.

        Args:
            _context (Context): context
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
