from bpy.utils import unregister_class, register_class
from .ui.main_panel import TBB_PT_MainPanel


bl_info = {
    "name": "Toolsbox Blender ",
    "description": "Toolsbox",
    "author": "",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Import",
    "wiki_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/wikis/home",
    "tracker_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/issues"
}

classes = (
    TBB_PT_MainPanel,
)

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)

