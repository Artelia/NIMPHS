# <pep8 compliant>
import os
from . import auto_load
from bpy.app import version as bl_version
from bpy.utils import previews
from bpy.types import Scene, Object
from bpy.props import PointerProperty
from bpy.app.handlers import frame_change_pre


bl_info = {
    "name": "Toolsbox OpenFOAM/TELEMAC",
    "description": "Load, visualize and manipulate OpenFOAM/TELEMAC files",
    "author": "Thibault Oudart, Félix Olart",
    "version": (0, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
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
               "The Toolsbox Blender addon depends on the numpy library.\n"
               "Unfortunately the Blender built you are using does not have this library.\n"
               "Please checkout the documentation to fix this issue (installation guide).")
    raise Exception(message)

try:
    import pyvista
except BaseException:
    pass

if "pyvista" not in globals():
    message = ("\n\n"
               "The Toolsbox Blender addon depends on the pyvista library.\n"
               "Unfortunately the Blender built you are using does not have this library.\n"
               "Please checkout the documentation to fix this issue (installation guide).")
    raise Exception(message)

if bl_version < (3, 0, 0):
    message = ("\n\n"
               "The Toolsbox Blender addon requires at least Blender 3.0.\n"
               "Your are using an older version.\n"
               "Please download the latest official release.")
    raise Exception(message)

# Register
from src.properties.shared.tbb_scene import TBB_Scene
from src.properties.shared.tbb_object import TBB_Object
from src.operators.openfoam.utils import update_openfoam_streaming_sequences
from src.panels.custom_progress_bar import register_custom_progress_bar

auto_load.init()


def register():
    auto_load.register()

    # Register custom properties
    Scene.tbb = PointerProperty(type=TBB_Scene)
    Object.tbb = PointerProperty(type=TBB_Object)

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_openfoam_streaming_sequences)

    # Add custom icons
    icons = previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons.load("openfoam", os.path.join(icons_dir, "openfoam_32_px.png"), 'IMAGE')
    icons.load("telemac", os.path.join(icons_dir, "telemac_32_px.png"), 'IMAGE')

    Scene.tbb_icons = {"main": icons}

    print("Registered Toolsbox OpenFOAM/TELEMAC")


def unregister():
    auto_load.unregister()

    # Remove icons
    for collection in Scene.tbb_icons.values():
        previews.remove(collection)
    Scene.tbb_icons.clear()

    print("Unregistered Toolsbox OpenFOAM/TELEMAC")
