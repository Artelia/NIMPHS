# <pep8 compliant>
from bpy.types import Panel, Context

from tbb.panels.utils import get_selected_object
from tbb.properties.utils import VariablesInformation


class TBB_PT_OpenfoamClip(Panel):
    """UI panel to manage clip settings used for previewing and creating sequences."""

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
        if obj is None:
            return False

        try:
            tmp_data = context.scene.tbb.tmp_data[obj.tbb.uid]
        except KeyError:
            return False

        return tmp_data is not None and tmp_data.is_ok()

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        tmp_data = context.scene.tbb.tmp_data[obj.tbb.uid]
        layout = self.layout

        # Check if we need to lock the ui
        lock_clip_settings = tmp_data.time_point != obj.tbb.settings.openfoam.preview_time_point
        enable_rows = not context.scene.tbb.create_sequence_is_running and not lock_clip_settings

        clip = obj.tbb.settings.openfoam.clip

        row = layout.row()
        row.enabled = enable_rows
        row.prop(clip, "type")

        if clip.type == 'SCALAR':

            if clip.scalar.name != 'NONE':
                row = layout.row()
                row.enabled = enable_rows
                row.prop(clip.scalar, "name")

                row = layout.row()
                row.enabled = enable_rows

                var_type = VariablesInformation(clip.scalar.name).get(0, prop='TYPE')

                if var_type == 'VECTOR':
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
