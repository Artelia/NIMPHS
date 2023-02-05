# <pep8 compliant>
import bpy
from bpy.utils import previews
from bpy.props import PointerProperty
from bpy.app import version as bl_version
from bpy.app.handlers import frame_change_pre, frame_change_post, save_pre
from bpy.types import Scene, Object, TOPBAR_MT_file_import, VIEW3D_MT_editor_menus, VIEW3D_HT_tool_header

import os
import json
from pathlib import Path

from . import auto_load

LOAD_INSTALLER = None

bl_info = {
    "name": "NIMPHS",
    "description": "Numerous Instruments to Manipulate and Post-process Hydraulic Simulations",
    "author": "Félix Olart, Thibault Oudart",
    "version": (0, 4, 2),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "warning": "This version is still in development.",
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "https://Artelia.github.io/NIMPHS/",
    "tracker_url": "https://github.com/Artelia/NIMPHS/issues"
}

if bl_version is not None and bl_version < (3, 0, 0):
    message = ("\n\n"
               "NIMPHS requires at least Blender 3.0.\n"
               "Your are using an older version.\n"
               "Please download the latest official release.")
    raise Exception(message)

# Load add-on state information
state_file_path = os.path.join(os.path.abspath(Path(__file__).parent), "nimphs.json")
with open(state_file_path, "r+", encoding='utf-8') as file:
    data = json.load(file)
    if data["installation"]["state"] == 'DONE':
        LOAD_INSTALLER = False
    elif data["installation"]["state"] == 'INSTALL':
        LOAD_INSTALLER = True
    else:
        message = ("\n\n"
                   "Unrecognized installation state.\n")
        raise Exception(message)

# Setup logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Proceed to normal imports (installation is done)
if LOAD_INSTALLER is False:
    from nimphs.menus.menus import nimphs_menus_draw
    from nimphs.properties.shared.nimphs_scene import NIMPHS_Scene
    from nimphs.properties.shared.nimphs_object import NIMPHS_Object
    from nimphs.operators.telemac.telemac_import_file import import_telemac_menu_draw
    from nimphs.operators.openfoam.openfoam_import_file import import_openfoam_menu_draw
    from nimphs.properties.utils.others import register_custom_progress_bar, nimphs_on_save_pre
    from nimphs.operators.utils.sequence import (
        update_openfoam_streaming_sequences,
        update_telemac_streaming_sequences,
        update_telemac_mesh_sequences,
    )

    auto_load.init()

else:
    from nimphs.properties.installer import NIMPHS_InstallerProperties
    from nimphs.panels.installer import NIMPHS_InstallerAddonPreferences
    from nimphs.operators.installer import NIMPHS_OT_Installer

    classes = (NIMPHS_InstallerProperties, NIMPHS_InstallerAddonPreferences, NIMPHS_OT_Installer)


def register() -> None:  # noqa: D103

    # File path to the 'state file' which stores information on the add-on's installation
    Scene.nimphs_state_file = state_file_path

    if LOAD_INSTALLER:

        for cls in classes:
            bpy.utils.register_class(cls)

    else:
        auto_load.register()

        # Register custom properties
        Scene.nimphs = PointerProperty(type=NIMPHS_Scene)
        Object.nimphs = PointerProperty(type=NIMPHS_Object)

        # Custom progress bar
        register_custom_progress_bar()

        # Custom app handlers
        frame_change_pre.append(update_openfoam_streaming_sequences)
        frame_change_pre.append(update_telemac_streaming_sequences)
        frame_change_post.append(update_telemac_mesh_sequences)
        save_pre.append(nimphs_on_save_pre)

        # Add custom icons
        icons = previews.new()
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        icons.load("openfoam", os.path.join(icons_dir, "openfoam_32_px.png"), 'IMAGE')
        icons.load("telemac", os.path.join(icons_dir, "telemac_32_px.png"), 'IMAGE')

        # Add custom import operators in 'File > Import'
        TOPBAR_MT_file_import.append(import_openfoam_menu_draw)
        TOPBAR_MT_file_import.append(import_telemac_menu_draw)
        # Add custom menus
        VIEW3D_MT_editor_menus.append(nimphs_menus_draw)

        # Setup logger using user preferences (this will affect all child loggers)
        prefs = bpy.context.preferences.addons[__package__].preferences.settings
        logger.setLevel(logging.getLevelName(prefs.log_level))

        Scene.nimphs_icons = {"main": icons}

        logger.debug("Registered NIMPHS")


def unregister() -> None:  # noqa: D103

    if LOAD_INSTALLER:
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

    else:
        # Reset default values (in case of unregister/register during execution of a modal operator)
        bpy.context.scene.nimphs.m_op_running = False
        bpy.context.scene.nimphs.m_op_value = -1.0
        bpy.context.scene.nimphs.m_op_label = ""

        # Reset draw function of VIEW3D_HT_tool_header
        VIEW3D_HT_tool_header.draw = NIMPHS_Scene.view_3d_ht_tool_header_draw

        auto_load.unregister()

        # Remove icons
        for collection in Scene.nimphs_icons.values():
            previews.remove(collection)
        Scene.nimphs_icons.clear()

        # Remove custom app handlers
        frame_change_pre.remove(update_openfoam_streaming_sequences)
        frame_change_pre.remove(update_telemac_streaming_sequences)
        frame_change_post.remove(update_telemac_mesh_sequences)
        save_pre.remove(nimphs_on_save_pre)

        # Remove custom import operators from 'File > Import'
        TOPBAR_MT_file_import.remove(import_openfoam_menu_draw)
        TOPBAR_MT_file_import.remove(import_telemac_menu_draw)
        # Remove custom menus
        VIEW3D_MT_editor_menus.remove(nimphs_menus_draw)

        logger.debug("Unregistered NIMPHS")
