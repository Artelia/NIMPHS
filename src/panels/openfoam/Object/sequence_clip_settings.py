# <pep8 compliant>
from bpy.types import Panel, Context


class TBB_PT_OpenfoamSequenceClipSettings(Panel):
    """
    UI panel to manage clip settings of the Streaming sequence.
    """

    bl_label = "Clip"
    bl_idname = "TBB_PT_OpenfoamSequenceClipSettings"
    bl_parent_id = "TBB_PT_OpenfoamSequenceSettings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        Determine whether to let the user access the panel or not.

        :type context: Context
        :rtype: bool
        """

        obj = context.active_object
        return obj.tbb_openfoam_sequence.update

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        obj = context.active_object
        clip = obj.tbb_openfoam_sequence.clip

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
