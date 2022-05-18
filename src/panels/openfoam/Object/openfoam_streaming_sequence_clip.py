# <pep8 compliant>
from bpy.types import Panel, Context

from src.panels.utils import get_selected_object


class TBB_PT_OpenfoamStreamingSequenceClip(Panel):
    """
    UI panel to manage clip settings of an OpenFOAM 'streaming sequence'.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_label = "Clip"
    bl_idname = "TBB_PT_OpenfoamStreamingSequenceClip"
    bl_parent_id = "TBB_PT_OpenfoamStreamingSequence"
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
        return obj.tbb.settings.openfoam.streaming_sequence.update

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        layout = self.layout
        obj = get_selected_object(context)
        clip = obj.tbb.settings.openfoam.streaming_sequence.clip

        row = layout.row()
        row.prop(clip, "type", text="Type")

        if clip.type == "scalar":
            if clip.scalar.name != "None@None":
                row = layout.row()
                row.prop(clip.scalar, "name", text="Scalars")

                value_type = clip.scalar.name.split("@")[1]
                if value_type == "vector_value":
                    row = layout.row()
                    row.prop(clip.scalar, "vector_value", text="Value")
                elif value_type == "value":
                    row = layout.row()
                    row.prop(clip.scalar, "value", text="Value")

                row = layout.row()
                row.prop(clip.scalar, "invert", text="Invert")
            else:
                row = layout.row()
                row.label(text="No data available.", icon='ERROR')
