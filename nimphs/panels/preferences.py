# <pep8 compliant>
from bpy.props import PointerProperty
from bpy.types import AddonPreferences, Context

import json

from nimphs.properties.preferences import NIMPHS_Preferences


class NIMPHS_Preferences(AddonPreferences):
    """UI panel to manage add-on's preferences."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = __package__.removesuffix(".panels")

    #: bpy.props.PointerProperty: Preferences of the addon.
    # Access through `context.preferences.addons['nimphs'].preferences.settings`.
    settings: PointerProperty(type=NIMPHS_Preferences)

    def draw(self, context: Context) -> None:
        """
        UI layout of this panel.

        Args:
            context (Context): context
        """

        # Files preferences
        box = self.layout.box()

        row = box.row()
        row.label(text="Files", icon='FILE')

        row = box.row()
        row.prop(self.settings, "openfoam_extensions", text="OpenFOAM")

        row = box.row()
        row.prop(self.settings, "telemac_extensions", text="TELEMAC")

        # System preferences
        box = self.layout.box()

        row = box.row()
        row.label(text="System", icon='PREFERENCES')

        row = box.row()
        row.prop(self.settings, "log_level", text="Log")

        with open(context.scene.nimphs_state_file, "r+", encoding='utf-8') as file:
            state = json.load(file)["installation"]["state"]

        row = box.row()

        if state == 'INSTALL':
            row.label(text="Installer state reset. Please re-open Blender to install.", icon='CHECKMARK')

        elif state == 'DONE':
            row.label(text="Installation:")
            row.operator("nimphs.reset_installer", text="Re-install", icon='FILE_REFRESH')
