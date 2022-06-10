# <pep8 compliant>
from bpy.types import Context, Panel

from tbb.panels.utils import get_selected_object


class TBB_PT_TelemacStreamingSequenceInterpolate(Panel):
    """UI panel to manage interpolation settings for TELEMAC 'streaming sequences'."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "Interpolate"
    bl_idname = "TBB_PT_TelemacStreamingSequenceInterpolate"
    bl_parent_id = "TBB_PT_TelemacStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        obj = get_selected_object(context)
        return obj.tbb.settings.telemac.s_sequence.update

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        layout = self.layout
        obj = get_selected_object(context)
        interpolation = obj.tbb.settings.telemac.s_sequence.interpolate

        row = layout.row()
        row.prop(interpolation, "type", text="Type")

        if interpolation.type != 'NONE':
            row = layout.row()
            row.prop(interpolation, "time_steps", text="Time steps")
