from bpy.utils import unregister_class, register_class
from bpy.types import Scene, Object
from bpy.props import PointerProperty
from bpy.app.handlers import frame_change_pre

from .operators.import_foam_file import TBB_OT_ImportFoamFile, TBB_OT_ReloadFoamFile
from .operators.preview import TBB_OT_Preview
from .operators.create_sequence import TBB_OT_CreateSequence
from .operators.utils import update_sequence_on_frame_change
from .panels.main_panel import TBB_PT_MainPanel
from .panels.clip import TBB_PT_Clip
from .panels.create_sequence import TBB_PT_CreateSequence
from .panels.progress_bar_create_sequence import register_custom_progress_bar
from .properties.settings import TBB_settings
from .properties.clip import TBB_clip_scalar, TBB_clip
from .properties.temporary_data import TBB_temporary_data
from .properties.sequence import TBB_sequence

bl_info = {
    "name": "Toolsbox Blender ",
    "description": "Toolsbox",
    "author": "",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "category": "Import",
    "doc_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/wikis/home",
    "tracker_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/issues"
}

operators = (
    TBB_OT_ImportFoamFile,
    TBB_OT_ReloadFoamFile,
    TBB_OT_Preview,
    TBB_OT_CreateSequence
)

panels = (
    TBB_PT_MainPanel,
    TBB_PT_Clip,
    TBB_PT_CreateSequence
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
    Scene.tbb_clip = PointerProperty(type=TBB_clip)
    Scene.tbb_temp_data = TBB_temporary_data()
    Object.tbb_sequence = PointerProperty(type=TBB_sequence)

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_sequence_on_frame_change)

def unregister():
    for category in reversed(classes):
        for cls in reversed(category):
            unregister_class(cls)

