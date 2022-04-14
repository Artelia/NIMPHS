# <pep8 compliant>
from bpy.types import Panel


class TBB_PT_OpenFOAMSequenceClipSettings(Panel):
    bl_label = "Clip"
    bl_idname = "TBB_PT_OpenFOAMSequenceClipSettings"
    bl_parent_id = "TBB_PT_OpenFOAMSequenceSettings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj.tbb_openfoam_sequence.update_on_frame_change

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        tbb_openfoam_sequence = obj.tbb_openfoam_sequence

        row = layout.row()
        row.prop(tbb_openfoam_sequence, "clip_type", text="Type")

        if tbb_openfoam_sequence.clip_type != "no_clip":
            row = layout.row()
            row.prop(tbb_openfoam_sequence, "clip_scalars", text="Scalars")

            value_type = tbb_openfoam_sequence.clip_scalars.split("@")[1]
            if value_type == "vector_value":
                row = layout.row()
                row.prop(tbb_openfoam_sequence, "clip_vector_value", text="Value")
            elif value_type == "value":
                row = layout.row()
                row.prop(tbb_openfoam_sequence, "clip_value", text="Value")

            row = layout.row()
            row.prop(tbb_openfoam_sequence, "clip_invert", text="Invert")
