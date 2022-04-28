# <pep8 compliant>
from bpy.utils import unregister_class, register_class
from bpy.types import Scene, Object
from bpy.props import PointerProperty, BoolProperty
from bpy.app.handlers import frame_change_pre

# OpenFOAM imports
from .operators.openfoam.Scene.import_file import TBB_OT_OpenfoamImportFile
from .operators.openfoam.Scene.reload_file import TBB_OT_OpenfoamReloadFile
from .operators.openfoam.Scene.preview import TBB_OT_OpenfoamPreview
from .operators.openfoam.Scene.create_sequence import TBB_OT_OpenfoamCreateSequence
from .operators.openfoam.utils import update_streaming_sequence
from .panels.openfoam.Scene.main_panel import TBB_PT_OpenfoamMainPanel
from .panels.openfoam.Scene.clip import TBB_PT_OpenfoamClip
from .panels.openfoam.Scene.create_sequence import TBB_PT_OpenfoamCreateSequence
from .panels.custom_progress_bar import register_custom_progress_bar
from .panels.openfoam.Object.sequence_settings import TBB_PT_OpenfoamSequenceSettings
from .panels.openfoam.Object.sequence_clip_settings import TBB_PT_OpenfoamSequenceClipSettings
from .properties.openfoam.Scene.settings import TBB_OpenfoamSettings
from .properties.openfoam.clip import TBB_OpenfoamClipProperty, TBB_OpenfoamClipScalarProperty
from .properties.openfoam.Object.sequence import TBB_OpenfoamSequenceProperty
from .properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData

# TELEMAC imports
from .operators.telemac.Scene.import_file import TBB_OT_TelemacImportFile
from .operators.telemac.Scene.reload_file import TBB_OT_TelemacReloadFile
from .operators.telemac.Scene.preview import TBB_OT_TelemacPreview
from .operators.telemac.Scene.create_sequence import TBB_OT_TelemacCreateSequence
from .panels.telemac.Scene.main_panel import TBB_PT_TelemacMainPanel
from .panels.telemac.Scene.create_sequence import TBB_PT_TelemacCreateSequence
from .properties.telemac.Scene.settings import TBB_TelemacSettings
from .properties.telemac.Object.sequence import TBB_TelemacSequenceProperty
from .properties.telemac.temporary_data import TBB_TelemacTemporaryData

# Other imports
from .panels.main_panel import TBB_PT_MainPanel
from .properties.scene_settings import TBB_SceneSettings
from .properties.sequence_settings import TBB_StreamingSequenceProperty

bl_info = {
    "name": "Toolsbox OpenFOAM/TELEMAC",
    "description": "Load, visualize and manipulate OpenFOAM/TELEMAC files",
    "author": "Thibault Oudart, Félix Olart",
    "version": (0, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "category": "Import",
    "doc_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/wikis/home",
    "tracker_url": "https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/issues"
}

operators = (
    TBB_OT_OpenfoamImportFile,
    TBB_OT_OpenfoamReloadFile,
    TBB_OT_OpenfoamPreview,
    TBB_OT_OpenfoamCreateSequence,
    TBB_OT_TelemacImportFile,
    TBB_OT_TelemacReloadFile,
    TBB_OT_TelemacPreview,
    TBB_OT_TelemacCreateSequence,
)

panels = (
    TBB_PT_MainPanel,
    TBB_PT_OpenfoamMainPanel,
    TBB_PT_OpenfoamClip,
    TBB_PT_OpenfoamCreateSequence,
    TBB_PT_OpenfoamSequenceSettings,
    TBB_PT_OpenfoamSequenceClipSettings,
    TBB_PT_TelemacMainPanel,
    TBB_PT_TelemacCreateSequence,
)

properties = (
    TBB_SceneSettings,
    TBB_StreamingSequenceProperty,
    TBB_OpenfoamClipScalarProperty,
    TBB_OpenfoamClipProperty,
    TBB_OpenfoamSettings,
    TBB_OpenfoamSequenceProperty,
    TBB_TelemacSettings,
    TBB_TelemacSequenceProperty,
)

classes = [operators, panels, properties]


def register():
    for category in classes:
        for cls in category:
            register_class(cls)

    # Register custom properties
    Scene.tbb_openfoam_tmp_data = TBB_OpenfoamTemporaryData()
    Scene.tbb_telemac_tmp_data = TBB_TelemacTemporaryData()
    Scene.tbb_openfoam_settings = PointerProperty(type=TBB_OpenfoamSettings)
    Scene.tbb_telemac_settings = PointerProperty(type=TBB_TelemacSettings)
    Object.tbb_openfoam_sequence = PointerProperty(type=TBB_OpenfoamSequenceProperty)
    Object.tbb_telemac_sequence = PointerProperty(type=TBB_TelemacSequenceProperty)
    Scene.tbb_create_sequence_is_running = BoolProperty(
        name="Create sequence state",
        description="State of the 'create sequence' operation (used by all the 'create sequence' operators)",
        default=False,
    )

    # Custom progress bar
    register_custom_progress_bar()

    # Custom app handlers
    frame_change_pre.append(update_streaming_sequence)


def unregister():
    for category in reversed(classes):
        for cls in reversed(category):
            unregister_class(cls)
