# <pep8 compliant>
from bpy.types import Panel, Object, Context

from ...properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_StreamingSequenceSettingsPanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC 'streaming sequence' settings.
    """

    @classmethod
    def poll(cls, context: Object) -> bool:
        """
        If false, hides the panel.

        :param obj: object
        :type obj: Object
        :rtype: bool
        """

        obj = context.active_object
        if obj is not None:
            return obj.tbb.is_streaming_sequence
        else:
            return False

    def draw(self, sequence_settings: TBB_ModuleStreamingSequenceSettings, obj: Object) -> None:
        """
        Layout of the panel.

        :param sequence_settings: 'streaming sequence' settings
        :type sequence_settings: TBB_StreamingSequenceProperty
        :param obj: object
        :type obj: Object
        """

        layout = self.layout

        row = layout.row()
        row.prop(obj.tbb, "update", text="Update")
        if obj.tbb.update:
            row = layout.row()
            row.prop(sequence_settings, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(sequence_settings, "anim_length", text="Length")

            row = layout.row()
            row.prop(sequence_settings, "import_point_data", text="Import point data")

            if sequence_settings.import_point_data:
                row = layout.row()
                row.prop(sequence_settings, "list_point_data", text="List")
