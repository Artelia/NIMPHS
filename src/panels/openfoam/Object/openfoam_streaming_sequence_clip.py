# <pep8 compliant>
from bpy.types import Panel, Context

from ...utils import get_selected_object


class TBB_PT_OpenfoamStreamingSequenceClip(Panel):
    """
    UI panel to manage clip settings of an OpenFOAM 'streaming sequence'.
    """

    bl_label = "Clip"
    bl_idname = "TBB_PT_OpenfoamSequenceClip"
    bl_parent_id = "TBB_PT_OpenfoamStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        obj = get_selected_object(context)
        return obj.tbb.settings.openfoam.update

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        obj = context.active_object
        clip = obj.tbb.settings.openfoam.clip

        row = layout.row()
        row.prop(clip, "type", text="Type")

        if clip.type == "scalar":
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
