# <pep8 compliant>
from bpy.types import Context

from ...shared.streaming_sequence_settings import TBB_StreamingSequenceSettingsPanel


class TBB_PT_OpenfoamStreamingSequence(TBB_StreamingSequenceSettingsPanel):
    """
    Main panel of the OpenFOAM 'streaming sequence' settings.
    This is the 'parent' panel.
    """

    bl_label = "OpenFOAM Streaming sequence"
    bl_idname = "TBB_PT_OpenfoamStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel. Calls 'super().poll(...)'.

        :type context: Context
        :rtype: bool
        """

        return super().poll(context)

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls 'super().draw(...)'.

        :type context: Context
        """

        obj = context.active_object
        if obj is not None:
            super().draw(obj.tbb.settings.openfoam, obj)
