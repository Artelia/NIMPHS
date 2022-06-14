# <pep8 compliant>
from bpy.types import Panel, Context, Object

from typing import Union
from tbb.operators.utils import get_temporary_data

from tbb.panels.utils import get_selected_object
from tbb.properties.shared.module_scene_settings import TBB_ModuleSceneSettings
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData


class TBB_CreateSequencePanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC modules.

    Specific settings are added in the classes which derive from this one.
    """

    register_cls = False
    is_custom_base_cls = True

    @classmethod
    def poll(cls, obj: Union[Object, None], context: Context) -> bool:
        """
        If false, hides the panel.

        Args:
            obj (Union[Object, None]): selected object
            context (Context): context

        Returns:
            bool: state
        """

        if obj is None:
            return False

        tmp_data = get_temporary_data(obj)
        return tmp_data is not None and tmp_data.is_ok() and not obj.tbb.is_streaming_sequence

    def draw(self, settings: TBB_ModuleSceneSettings, context: Context) -> bool:
        """
        Layout of the panel.

        Args:
            settings (TBB_ModuleSceneSettings): scene settings
            context (Context): context

        Returns:
            bool: enable rows
        """

        layout = self.layout

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb.create_sequence_is_running

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_type", text="Type")

        if settings.sequence_type == "mesh_sequence":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["start_time_point"]', text="Start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["end_time_point"]', text="End")
        elif settings.sequence_type == "streaming_sequence":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "frame_start", text="Frame start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["anim_length"]', text="Length")
        else:
            row = layout.row()
            row.label(text="Error: unknown sequence type...", icon='ERROR')

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "import_point_data")

        if settings.import_point_data:
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "point_data", text="List")

        return enable_rows
