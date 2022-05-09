# <pep8 compliant>
from . import auto_load
from bpy.utils import previews
from bpy.types import Scene, Object
from bpy.props import PointerProperty
from bpy.app.handlers import frame_change_pre
from os import path

from src.operators.openfoam.utils import update_streaming_sequence
from src.panels.custom_progress_bar import register_custom_progress_bar
from src.properties.shared.tbb_scene import TBB_Scene
from src.properties.shared.tbb_object import TBB_Object

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

auto_load.init()


def register():
    auto_load.register()

    # Register custom properties
    Scene.tbb = PointerProperty(type=TBB_Scene)
    Object.tbb = PointerProperty(type=TBB_Object)

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_streaming_sequence)

    # Add custom icons
    icons = previews.new()
    icons_dir = path.join(path.dirname(__file__), "icons")
    icons.load("openfoam", path.join(icons_dir, "openfoam_32_px.png"), 'IMAGE')
    icons.load("telemac", path.join(icons_dir, "telemac_32_px.png"), 'IMAGE')

    Scene.tbb_icons = {"main": icons}

    print("Registered Toolsbox OpenFOAM/TELEMAC")


def unregister():
    auto_load.unregister()

    # Remove icons
    for collection in Scene.tbb_icons.values():
        previews.remove(collection)
    Scene.tbb_icons.clear()

    print("Unregistered Toolsbox OpenFOAM/TELEMAC")
