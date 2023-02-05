# <pep8 compliant>
# <pep8 compliant>
from bpy.props import PointerProperty
from bpy.types import AddonPreferences, Context

import json

from nimphs.properties.installer import NIMPHS_InstallerProperties


class NIMPHS_InstallerAddonPreferences(AddonPreferences):
    """UI panel to manage dependencies installation of the add-on."""

    register_cls = False
    is_custom_base_cls = False

    bl_idname = __package__.removesuffix(".panels")

    #: bpy.props.PointerProperty: Installation configuration of the add-on.
    # When the installer is loaded, access through `context.preferences.addons['nimphs'].preferences.settings`.
    settings: PointerProperty(type=NIMPHS_InstallerProperties)

    def draw(self, _context: Context) -> None:
        """
        UI layout of this panel.

        Args:
            _context (Context): context
        """

        # Installation configuration
        box = self.layout.box()

        row = box.row()
        row.label(text="Installation")

        with open(self.settings.state_file, "r+", encoding='utf-8') as file:
            state = json.load(file)["installation"]["state"]

        if state == 'INSTALL':

            row = box.row()
            row.prop(self.settings, "configuration", text="Configuration")

            row = box.row()
            row.operator("nimphs.install", text="Install")

        else:

            row = box.row()
            row.label(text="Installation complete, please re-open Blender.", icon='CHECKMARK')
