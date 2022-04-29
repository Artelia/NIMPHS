# <pep8 compliant>
from bpy.types import Panel, Context

from ...utils import get_selected_object


class TBB_PT_OpenfoamClip(Panel):
    """
    UI panel to manage clip settings used for previewing and creating sequences.
    """

    bl_label = "Clip"
    bl_idname = "TBB_PT_OpenfoamClip"
    bl_parent_id = "TBB_PT_OpenfoamMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        obj = get_selected_object(context)

        if obj is None:
            return context.scene.tbb_openfoam_tmp_data.is_ok()
        else:
            return context.scene.tbb_openfoam_tmp_data.is_ok() and not obj.tbb_openfoam_sequence.is_streaming_sequence

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        settings = context.scene.tbb_openfoam_settings
        tmp_data = context.scene.tbb_openfoam_tmp_data
        clip = context.scene.tbb_openfoam_settings.clip

        # Check if temp mesh data is loaded. If not, do not show clip settings and show a message asking to hit preview.
        if tmp_data.time_point != settings["preview_time_point"]:
            lock_clip_settings = True
        else:
            lock_clip_settings = False

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb_create_sequence_is_running and not lock_clip_settings

        row = layout.row()
        row.enabled = enable_rows
        row.prop(clip, "type")

        if clip.type == "scalar":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(clip.scalar, "name")

            row = layout.row()
            row.enabled = enable_rows

            is_vector_scalars = clip.scalar.name.split("@")[1] == "vector_value"
            if is_vector_scalars:
                row.prop(clip.scalar, "vector_value", text="Value")
            else:
                row.prop(clip.scalar, "value", text="Value")

            row = layout.row()
            row.enabled = enable_rows
            row.prop(clip.scalar, "invert")

        if lock_clip_settings:
            row = layout.row()
            row.label(text="Error: no data available at this time point. Please reload or hit 'preview'.", icon="ERROR")
