# <pep8 compliant>
from bpy.types import Panel, Object, Context

from ...properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings
from ..utils import get_selected_object


class TBB_StreamingSequenceSettingsPanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC 'streaming sequence' settings.
    """

    @classmethod
    def poll(cls, context: Context, type: str) -> bool:
        """
        If false, hides the panel.

        :param obj: object
        :type obj: Object
        :rtype: bool
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.tbb.is_streaming_sequence and obj.tbb.settings.module == type
        else:
            return False

    def draw(self, sequence_settings: TBB_ModuleStreamingSequenceSettings) -> None:
        """
        Layout of the panel.

        :param sequence_settings: 'streaming sequence' settings
        :type sequence_settings: TBB_StreamingSequenceProperty
        """

        layout = self.layout

        row = layout.row()
        row.prop(sequence_settings, "update", text="Update")
        if sequence_settings.update:
            row = layout.row()
            row.prop(sequence_settings, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(sequence_settings, "anim_length", text="Length")

            row = layout.row()
            row.prop(sequence_settings, "import_point_data", text="Import point data")

            if sequence_settings.import_point_data:
                row = layout.row()
                row.prop(sequence_settings, "list_point_data", text="List")
