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

        layout = self.layout

        obj = get_selected_object(context)
        if obj is not None:
            obj_settings = obj.tbb.settings.telemac.streaming_sequence
            super().draw(obj_settings)

            if obj_settings.update:
                row = layout.row()
                row.prop(obj_settings, "normalize", text="Normalize")
