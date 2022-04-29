# <pep8 compliant>
from bpy.types import Panel


class StreamingSequenceSettingsPanel(Panel):
    """
    Main panel of the 'Streaming sequence' settings. This is the 'parent' panel.
    """

    @classmethod
    def poll(cls, sequence_settings) -> bool:
        """
        If false, hides the panel.

        :rtype: bool
        """

        return sequence_settings.is_streaming_sequence

    def draw(self, sequence_settings) -> None:
        """
        Layout of the panel.
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
