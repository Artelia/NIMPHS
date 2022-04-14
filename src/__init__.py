# <pep8 compliant>
from bpy.utils import unregister_class, register_class
from bpy.types import Scene, Object
from bpy.props import PointerProperty
from bpy.app.handlers import frame_change_pre

# OpenFOAM imports
from .operators.OpenFOAM.Scene.import_file import TBB_OT_OpenFOAMImportFile
from .operators.OpenFOAM.Scene.reload_file import TBB_OT_OpenFOAMReloadFile
from .operators.OpenFOAM.Scene.preview import TBB_OT_OpenFOAMPreview
from .operators.OpenFOAM.Scene.create_sequence import TBB_OT_OpenFOAMCreateSequence
from .operators.OpenFOAM.utils import update_sequence_on_frame_change
from .panels.OpenFOAM.Scene.main_panel import TBB_PT_OpenFOAMMainPanel
from .panels.OpenFOAM.Scene.clip import TBB_PT_OpenFOAMClip
from .panels.OpenFOAM.Scene.create_sequence import TBB_PT_OpenFOAMCreateSequence
from .panels.custom_progress_bar import register_custom_progress_bar
from .panels.OpenFOAM.Object.sequence_settings import TBB_PT_OpenFOAMSequenceSettings
from .panels.OpenFOAM.Object.sequence_clip_settings import TBB_PT_OpenFOAMSequenceClipSettings
from .properties.OpenFOAM.Scene.settings import TBB_OpenFOAMSettings
from .properties.OpenFOAM.Scene.clip import TBB_OpenFOAMClipProperty, TBB_OpenFOAMClipScalarProperty
from .properties.temporary_data import TBB_OpenFOAMTemporaryData
from .properties.OpenFOAM.Object.sequence import TBB_OpenFOAMSequenceProperty

bl_info = {
    "name": "Toolsbox OpenFOAM/TELEMAC",
    "description": "Load, visualize and manipulate OpenFOAM files",
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
    TBB_OT_OpenFOAMImportFile,
    TBB_OT_OpenFOAMReloadFile,
    TBB_OT_OpenFOAMPreview,
    TBB_OT_OpenFOAMCreateSequence
)

panels = (
    TBB_PT_OpenFOAMMainPanel,
    TBB_PT_OpenFOAMClip,
    TBB_PT_OpenFOAMCreateSequence,
    TBB_PT_OpenFOAMSequenceSettings,
    TBB_PT_OpenFOAMSequenceClipSettings
)

properties = (
    TBB_OpenFOAMSettings,
    TBB_OpenFOAMClipScalarProperty,
    TBB_OpenFOAMClipProperty,
    TBB_OpenFOAMSequenceProperty
)

classes = [operators, panels, properties]


def register():
    for category in classes:
        for cls in category:
            register_class(cls)

    # Register custom properties
    Scene.tbb_openfoam_tmp_data = TBB_OpenFOAMTemporaryData()
    Scene.tbb_openfoam_settings = PointerProperty(type=TBB_OpenFOAMSettings)
    Scene.tbb_openfoam_clip = PointerProperty(type=TBB_OpenFOAMClipProperty)
    Object.tbb_openfoam_sequence = PointerProperty(type=TBB_OpenFOAMSequenceProperty)

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_sequence_on_frame_change)


def unregister():
    for category in reversed(classes):
        for cls in reversed(category):
            unregister_class(cls)
