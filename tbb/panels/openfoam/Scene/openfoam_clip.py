# <pep8 compliant>
from bpy.types import Panel, Context

from tbb.panels.utils import get_selected_object


class TBB_PT_OpenfoamClip(Panel):
    """
    UI panel to manage clip settings used for previewing and creating sequences.
    """
    register_cls = True
    is_custom_base_cls = False

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

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        obj = get_selected_object(context)

        tmp_data = context.scene.tbb.settings.openfoam.tmp_data
        if obj is None:
            return tmp_data.is_ok()
        else:
            return tmp_data.is_ok() and not obj.tbb.is_streaming_sequence

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        layout = self.layout
        settings = context.scene.tbb.settings.openfoam
        tmp_data = settings.tmp_data
        clip = context.scene.tbb.settings.openfoam.clip

        # Check if temp mesh data is loaded. If not, do not show clip settings and show a message asking to hit preview.
        if tmp_data.time_point != settings["preview_time_point"]:
            lock_clip_settings = True
        else:
            lock_clip_settings = False

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb.create_sequence_is_running and not lock_clip_settings

        row = layout.row()
        row.enabled = enable_rows
        row.prop(clip, "type")

        if clip.type == "scalar":

            if clip.scalar.name != "None@None":
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
            else:
                row = layout.row()
                row.label(text="No data available.", icon='ERROR')

        if lock_clip_settings:
            row = layout.row()
            row.label(text="Error: no data available at this time point. Please reload or hit 'preview'.", icon='ERROR')
