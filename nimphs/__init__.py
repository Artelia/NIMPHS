# <pep8 compliant>
import bpy
from bpy.utils import previews
from bpy.props import PointerProperty
from bpy.app import version as bl_version
from bpy.app.handlers import frame_change_pre, frame_change_post, save_pre
from bpy.types import Scene, Object, TOPBAR_MT_file_import, VIEW3D_MT_editor_menus

import os

from . import auto_load

bl_info = {
    "name": "NIMPHS",
    "description": "Numerous Instruments to Manipulate and Post-process Hydraulic Simulations",
    "author": "Félix Olart, Thibault Oudart",
    "version": (0, 4, 0),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "warning": "This version is still in development.",
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "https://github.com/Artelia/NIMPHS/issues"
}

# Test environment, inspired from:
# https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/__init__.py
# current_directory = os.path.dirname(os.path.abspath(__file__))
# addons_directory = os.path.dirname(current_directory)
# addon_name = os.path.basename(current_directory)

if bl_version is not None and bl_version < (3, 0, 0):
    message = ("\n\n"
               "NIMPHS requires at least Blender 3.0.\n"
               "Your are using an older version.\n"
               "Please download the latest official release.")
    raise Exception(message)

try:
    import pyvista
except BaseException:
    pass

if "pyvista" not in globals():
    message = ("\n\n"
               "NIMPHS depends on the pyvista library.\n"
               "Unfortunately the Blender built you are using does not have this library.\n"
               "Please checkout the documentation to fix this issue (installation guide).")
    raise Exception(message)

# Register
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

# Setup logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


auto_load.init()


def register() -> None:  # noqa: D103
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
