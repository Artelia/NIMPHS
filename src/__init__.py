from bpy.utils import unregister_class, register_class
from bpy.types import Scene
from bpy.props import PointerProperty

from .operators.import_foam_file import TBB_OT_ImportFoamFile, TBB_OT_ReloadFoamFile
from .operators.preview import TBB_OT_Preview
from .panels.main_panel import TBB_PT_MainPanel
from .properties.settings import TBB_settings
from .properties.clip import TBB_clip_scalar, TBB_clip

bl_info = {
    "name": "Toolsbox Blender ",
    "description": "Toolsbox",
    "author": "",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "category": "Import",
    "wiki_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/wikis/home",
    "tracker_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/issues"
}

operators = (
    TBB_OT_ImportFoamFile,
    TBB_OT_ReloadFoamFile,
    TBB_OT_Preview,
)

panels = (
    TBB_PT_MainPanel,
)

properties = (
    TBB_settings,
    TBB_clip_scalar,
    TBB_clip
)

classes = [operators, panels, properties]

def register():
    for category in classes:
        for cls in category:
            register_class(cls)
    
    # Register custom properties
    Scene.tbb_settings = PointerProperty(type=TBB_settings)

def unregister():
    for category in reversed(classes):
        for cls in reversed(category):
            unregister_class(cls)

