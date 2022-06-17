# <pep8 compliant>
from bpy.types import Context

from tbb.panels.utils import get_selected_object
from tbb.panels.shared.streaming_sequence_settings import TBB_StreamingSequenceSettingsPanel


class TBB_PT_TelemacStreamingSequence(TBB_StreamingSequenceSettingsPanel):
    """
    Main panel of the TELEMAC 'streaming sequence' settings.

    This is the 'parent' panel.
    """

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC Streaming sequence"
    bl_idname = "TBB_PT_TelemacStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel. Calls parent poll function.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context, "TELEMAC")

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls parent draw function.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        sequence = obj.tbb.settings.telemac.s_sequence

        # Display file_path information
        box = self.layout.box()
        row = box.row()
        row.label(text=f"File: {obj.tbb.settings.file_path}")
        row.operator("tbb.edit_file_path", text="", icon="GREASEPENCIL")

        try:
            tmp_data = context.scene.tbb.tmp_data[obj.tbb.uid]
        except KeyError:
            tmp_data = None

        # Check temporary data
        if tmp_data is None or not tmp_data.is_ok():
            row = self.layout.row()
            row.label(text="Reload data: ", icon='ERROR')
            row.operator("tbb.reload_telemac_file", text="Reload", icon='FILE_REFRESH')
            return

        row = self.layout.row()
        row.prop(sequence, "update", text="Update")

        if sequence.update:
            # Import settings
            interpolate = obj.tbb.settings.telemac.interpolate

            box = self.layout.box()
            row = box.row()
            row.label(text="Interpolation")

            row = box.row()
            row.prop(interpolate, "type", text="Type")

            if interpolate.type != 'NONE':
                row = box.row()
                row.prop(interpolate, "time_steps", text="Time steps")

            # Point data and sequence settings
            super().draw(context, obj, sequence)
