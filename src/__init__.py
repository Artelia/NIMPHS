# <pep8 compliant>
from bpy.utils import unregister_class, register_class
from bpy.types import Scene, Object
from bpy.props import PointerProperty, BoolProperty
from bpy.app.handlers import frame_change_pre

# OpenFOAM imports
from .operators.openfoam.Scene.openfoam_import_file import TBB_OT_OpenfoamImportFile
from .operators.openfoam.Scene.openfoam_reload_file import TBB_OT_OpenfoamReloadFile
from .operators.openfoam.Scene.openfoam_preview import TBB_OT_OpenfoamPreview
from .operators.openfoam.Scene.openfoam_create_sequence import TBB_OT_OpenfoamCreateSequence
from .operators.openfoam.utils import update_streaming_sequence
from .panels.openfoam.Scene.openfoam_main_panel import TBB_PT_OpenfoamMainPanel
from .panels.openfoam.Scene.clip import TBB_PT_OpenfoamClip
from .panels.openfoam.Scene.openfoam_create_sequence import TBB_PT_OpenfoamCreateSequence
from .panels.custom_progress_bar import register_custom_progress_bar
from .panels.openfoam.Object.openfoam_streaming_sequence import TBB_PT_OpenfoamStreamingSequence
from .panels.openfoam.Object.openfoam_streaming_sequence_clip import TBB_PT_OpenfoamStreamingSequenceClip
from .properties.openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings
from .properties.openfoam.clip import TBB_OpenfoamClipProperty, TBB_OpenfoamClipScalarProperty
from .properties.openfoam.Object.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty
from .properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData

# TELEMAC imports
from .operators.telemac.Scene.telemac_import_file import TBB_OT_TelemacImportFile
from .operators.telemac.Scene.telemac_reload_file import TBB_OT_TelemacReloadFile
from .operators.telemac.Scene.telemac_preview import TBB_OT_TelemacPreview
from .operators.telemac.Scene.telemac_create_sequence import TBB_OT_TelemacCreateSequence
from .panels.telemac.Scene.telemac_main_panel import TBB_PT_TelemacMainPanel
from .panels.telemac.Scene.telemac_create_sequence import TBB_PT_TelemacCreateSequence
from .properties.telemac.Scene.telemac_settings import TBB_TelemacSettings
from .properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from .properties.telemac.temporary_data import TBB_TelemacTemporaryData

# Other imports
from .properties.shared.tbb_settings import TBB_Settings
from .properties.shared.scene_settings import TBB_ModuleSceneSettings
from .properties.shared.streaming_sequence_property import TBB_StreamingSequenceProperty

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
    TBB_PT_OpenfoamMainPanel,
    TBB_PT_OpenfoamClip,
    TBB_PT_OpenfoamCreateSequence,
    TBB_PT_OpenfoamStreamingSequence,
    TBB_PT_OpenfoamStreamingSequenceClip,
    TBB_PT_TelemacMainPanel,
    TBB_PT_TelemacCreateSequence,
)

properties = (
    TBB_ModuleSceneSettings,
    TBB_StreamingSequenceProperty,
    TBB_OpenfoamClipScalarProperty,
    TBB_OpenfoamClipProperty,
    TBB_OpenfoamSettings,
    TBB_OpenfoamStreamingSequenceProperty,
    TBB_TelemacSettings,
    TBB_TelemacStreamingSequenceProperty,
    TBB_Settings,
)

classes = [operators, panels, properties]


def register():
    for category in classes:
        for cls in category:
            register_class(cls)

    # Register custom properties
    Scene.tbb_settings = PointerProperty(type=TBB_Settings)
    Object.tbb_openfoam_sequence = PointerProperty(type=TBB_OpenfoamStreamingSequenceProperty)
    Object.tbb_telemac_sequence = PointerProperty(type=TBB_TelemacStreamingSequenceProperty)
    Scene.tbb_create_sequence_is_running = BoolProperty(
        name="Create sequence state",
        description="State of the 'create sequence' operation (used by all 'create sequence' operators)",
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
