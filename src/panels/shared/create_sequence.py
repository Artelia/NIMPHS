# <pep8 compliant>
from bpy.types import Panel, Context

from ..utils import get_selected_object


class CreateSequencePanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC modules. Specific settings are added in the classes which derive from this one.
    """

    @classmethod
    def poll(cls, tmp_data, context: Context) -> bool:
        """
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        obj = get_selected_object(context)

        if obj is None:
            return tmp_data.is_ok()
        else:
            if tmp_data.module_name == "TELEMAC":
                return tmp_data.is_ok() and not obj.tbb_telemac_sequence.is_streaming_sequence
            elif tmp_data.module_name == "OpenFOAM":
                return tmp_data.is_ok() and not obj.tbb_openfoam_sequence.is_streaming_sequence
            else:
                return tmp_data.is_ok()

    def draw(self, settings, context: Context) -> bool:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb_create_sequence_is_running

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_type", text="Type")

        if settings.sequence_type == "mesh_sequence":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["start_time_point"]', text="Start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["end_time_point"]', text="End")
        elif settings.sequence_type == "streaming_sequence":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "frame_start", text="Frame start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["anim_length"]', text="Length")
        else:
            row = layout.row()
            row.label(text="Error: unknown sequence type...", icon="ERROR")

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "import_point_data")

        if settings.import_point_data:
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "list_point_data", text="List")

        return enable_rows
