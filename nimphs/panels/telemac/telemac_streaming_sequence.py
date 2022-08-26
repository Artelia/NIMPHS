# <pep8 compliant>
from bpy.types import Context

from nimphs.panels.utils import get_selected_object
from nimphs.panels.shared.streaming_sequence_settings import NIMPHS_StreamingSequenceSettingsPanel


class NIMPHS_PT_TelemacStreamingSequence(NIMPHS_StreamingSequenceSettingsPanel):
    """Main panel of the TELEMAC 'streaming sequence' settings."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC Streaming sequence"
    bl_idname = "NIMPHS_PT_TelemacStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context, 'TELEMAC')

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        sequence = obj.nimphs.settings.telemac.s_sequence

        # Display file_path information
        box = self.layout.box()
        row = box.row()
        row.label(text=f"File: {obj.nimphs.settings.file_path}")
        row.operator("nimphs.edit_file_path", text="", icon="GREASEPENCIL")

        file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)

        # Check file data
        if file_data is None or not file_data.is_ok():
            row = self.layout.row()
            row.label(text="Reload data: ", icon='ERROR')
            row.operator("nimphs.reload_telemac_file", text="Reload", icon='FILE_REFRESH')
            return

        row = self.layout.row()
        row.prop(sequence, "update", text="Update")

        if sequence.update:
            # Import settings
            interpolate = obj.nimphs.settings.telemac.interpolate

            box = self.layout.box()
            row = box.row()
            row.label(text="Interpolation")

            row = box.row()
            row.prop(interpolate, "type", text="Type")

            if interpolate.type != 'NONE':
                row = box.row()
                row.prop(interpolate, "steps", text="Time steps")

            # Point data and sequence settings
            super().draw(context, obj, sequence)
