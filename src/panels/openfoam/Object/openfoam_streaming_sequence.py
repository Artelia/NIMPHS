# <pep8 compliant>
from bpy.types import Context

from ...shared.streaming_sequence_settings import StreamingSequenceSettingsPanel


class TBB_PT_OpenfoamStreamingSequence(StreamingSequenceSettingsPanel):
    """
    Main panel of the 'Streaming sequence' settings. This is the 'parent' panel.
    """

    bl_label = "OpenFOAM Streaming sequence"
    bl_idname = "TBB_PT_OpenfoamStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        obj = context.active_object
        if obj is not None:
            return super().poll(obj.tbb_openfoam_sequence)
        else:
            return False

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        obj = context.active_object
        if obj is not None:
            super().draw(obj.tbb_openfoam_sequence)
