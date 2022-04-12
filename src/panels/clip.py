from bpy.types import Panel

class TBB_PT_Clip(Panel):
    bl_label = "Clip"
    bl_idname = "TBB_PT_Clip"
    bl_parent_id = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene.tbb_temp_data.is_ok()

    def draw(self,context):
        layout = self.layout
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        temp_mesh_data = context.scene.tbb_temp_data.mesh_data
        # Check if temp mesh data is loaded. If not, do not show clip settings and show a message asking to reload the file.
        if temp_mesh_data != None:
            is_vector_scalars = len(temp_mesh_data.get_array(clip.scalars_props.scalars, preference="point").shape) == 2
            show_clip_settings = True
        else: show_clip_settings = False

        row = layout.row()
        row.enabled = not settings.create_sequence_is_running
        row.prop(clip, "type")

        if show_clip_settings and clip.type == "scalar":
            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.prop(clip.scalars_props, "scalars")

            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            if is_vector_scalars:
                row.prop(clip.scalars_props, '["vector_value"]', text="Value")
            else:
                row.prop(clip.scalars_props, '["value"]', text="Value")

            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.prop(clip.scalars_props, "invert")