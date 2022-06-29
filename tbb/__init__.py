# <pep8 compliant>
import bpy
from bpy.utils import previews
from bpy.props import PointerProperty
from bpy.app import version as bl_version
from bpy.app.handlers import frame_change_pre, frame_change_post, save_pre
from bpy.types import Scene, Object, TOPBAR_MT_file_import, VIEW3D_MT_editor_menus

# Remove error on building the docs, since fake-bpy-module defines version as 'None'
if bl_version is None:
    bl_version = (3, 0, 0)

import os
from . import auto_load

bl_info = {
    "name": "Toolbox OpenFOAM/TELEMAC",
    "description": "Load, visualize and manipulate OpenFOAM/TELEMAC files",
    "author": "Thibault Oudart, Félix Olart",
    "version": (0, 4, 0),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "warning": "This version is still in development.",
    "category": "Import",
    "doc_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/wikis/home",
    "tracker_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/issues"
}

# Test environment, inspired from:
# https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/__init__.py
# current_directory = os.path.dirname(os.path.abspath(__file__))
# addons_directory = os.path.dirname(current_directory)
# addon_name = os.path.basename(current_directory)

try:
    import numpy
except BaseException:
    pass

if "numpy" not in globals():
    message = ("\n\n"
               "The Toolbox Blender addon depends on the numpy library.\n"
               "Unfortunately the Blender built you are using does not have this library.\n"
               "Please checkout the documentation to fix this issue (installation guide).")
    raise Exception(message)

try:
    import pyvista
except BaseException:
    pass

if "pyvista" not in globals():
    message = ("\n\n"
               "The Toolbox Blender addon depends on the pyvista library.\n"
               "Unfortunately the Blender built you are using does not have this library.\n"
               "Please checkout the documentation to fix this issue (installation guide).")
    raise Exception(message)

if bl_version < (3, 0, 0):
    message = ("\n\n"
               "The Toolbox Blender addon requires at least Blender 3.0.\n"
               "Your are using an older version.\n"
               "Please download the latest official release.")
    raise Exception(message)

# Register
from tbb.menus.menus import tbb_menus_draw
from tbb.properties.shared.tbb_scene import TBB_Scene
from tbb.properties.shared.tbb_object import TBB_Object
from tbb.operators.openfoam.utils import update_openfoam_streaming_sequences
from tbb.properties.utils import register_custom_progress_bar, tbb_on_save_pre
from tbb.operators.telemac.Scene.telemac_import_file import import_telemac_menu_draw
from tbb.operators.openfoam.Scene.openfoam_import_file import import_openfoam_menu_draw
from tbb.operators.telemac.utils import update_telemac_streaming_sequences, update_telemac_mesh_sequences

# Setup logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

auto_load.init()


def register() -> None:  # noqa: D103
    auto_load.register()

    # Register custom properties
    Scene.tbb = PointerProperty(type=TBB_Scene)
    Object.tbb = PointerProperty(type=TBB_Object)

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_openfoam_streaming_sequences)
    frame_change_pre.append(update_telemac_streaming_sequences)
    frame_change_post.append(update_telemac_mesh_sequences)
    save_pre.append(tbb_on_save_pre)

    # Add custom icons
    icons = previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons.load("openfoam", os.path.join(icons_dir, "openfoam_32_px.png"), 'IMAGE')
    icons.load("telemac", os.path.join(icons_dir, "telemac_32_px.png"), 'IMAGE')

    # Add custom import operators in 'File > Import'
    TOPBAR_MT_file_import.append(import_openfoam_menu_draw)
    TOPBAR_MT_file_import.append(import_telemac_menu_draw)
    # Add custom menus
    VIEW3D_MT_editor_menus.append(tbb_menus_draw)

    # Setup logger using user preferences (this will affect all child loggers)
    prefs = bpy.context.preferences.addons[__package__].preferences.settings
    logger.setLevel(logging.getLevelName(prefs.log_level))

    Scene.tbb_icons = {"main": icons}

    logger.debug("Registered Toolbox OpenFOAM/TELEMAC")


def unregister() -> None:  # noqa: D103
    auto_load.unregister()

    # Remove icons
    for collection in Scene.tbb_icons.values():
        previews.remove(collection)
    Scene.tbb_icons.clear()

    # Remove custom app handlers
    frame_change_pre.remove(update_openfoam_streaming_sequences)
    frame_change_pre.remove(update_telemac_streaming_sequences)
    frame_change_post.remove(update_telemac_mesh_sequences)
    save_pre.remove(tbb_on_save_pre)

    # Remove custom import operators from 'File > Import'
    TOPBAR_MT_file_import.remove(import_openfoam_menu_draw)
    TOPBAR_MT_file_import.remove(import_telemac_menu_draw)
    # Remove custom menus
    VIEW3D_MT_editor_menus.remove(tbb_menus_draw)

    logger.debug("Unregistered Toolbox OpenFOAM/TELEMAC")
