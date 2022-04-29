# <pep8 compliant>
from bpy.types import Panel

from ...properties.shared.streaming_sequence_property import TBB_StreamingSequenceProperty


class TBB_StreamingSequenceSettingsPanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC 'streaming sequence' settings.
    """

    @classmethod
    def poll(cls, sequence_settings: TBB_StreamingSequenceProperty) -> bool:
        """
        If false, hides the panel.

        :param sequence_settings: 'streaming sequence' settings
        :type sequence_settings: TBB_StreamingSequenceProperty
        :rtype: bool
        """

        return sequence_settings.is_streaming_sequence

    def draw(self, sequence_settings: TBB_StreamingSequenceProperty) -> None:
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
