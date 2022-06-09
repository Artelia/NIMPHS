# <pep8 compliant>
from bpy.types import Context

from tbb.panels.utils import get_selected_object
from tbb.panels.shared.streaming_sequence_settings import TBB_StreamingSequenceSettingsPanel


class TBB_PT_OpenfoamStreamingSequence(TBB_StreamingSequenceSettingsPanel):
    """
    Main panel of the OpenFOAM 'streaming sequence' settings.

    This is the 'parent' panel.
    """

    register_cls = True
    is_custom_base_cls = False

    bl_label = "OpenFOAM Streaming sequence"
    bl_idname = "TBB_PT_OpenfoamStreamingSequence"
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

        return super().poll(context, "OpenFOAM")

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls parent draw function.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        if obj is not None:
            seq_settings = obj.tbb.settings.openfoam.streaming_sequence
            super().draw(seq_settings)

            if seq_settings.update:
                layout = self.layout

                row = layout.row()
                row.prop(seq_settings, "decompose_polyhedra", text="Decompose polyhedra")
                row = layout.row()
                row.prop(seq_settings, "triangulate", text="Triangulate")
                row = layout.row()
                row.prop(seq_settings, "case_type", text="Case")
