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
        obj = context.active_object
        # Even if no objects are selected, the last selected object remains in the active_objects variable
        if len(context.selected_objects) == 0:
            obj = None
            
        if obj == None:
            return context.scene.tbb_temp_data.is_ok()
        else:
            return context.scene.tbb_temp_data.is_ok() and not obj.tbb_openfoam_sequence.is_on_frame_change_sequence

    def draw(self,context):
        layout = self.layout
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        temp_data = context.scene.tbb_temp_data

        # Check if temp mesh data is loaded. If not, do not show clip settings and show a message asking to hit preview.
        if temp_data.time_step != settings["preview_time_point"]: lock_clip_settings = True
        else: lock_clip_settings = False

        # Check if we need to lock the ui
        enable_rows = not settings.create_sequence_is_running and not lock_clip_settings

        row = layout.row()
        row.enabled = enable_rows
        row.prop(clip, "type")

        if clip.type == "scalar":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(clip.scalars_props, "scalars")

            row = layout.row()
            row.enabled = enable_rows

            is_vector_scalars = clip.scalars_props.scalars.split("@")[1] == "vector_value"
            if is_vector_scalars:
                row.prop(clip.scalars_props, '["vector_value"]', text="Value")
            else:
                row.prop(clip.scalars_props, '["value"]', text="Value")

            row = layout.row()
            row.enabled = enable_rows
            row.prop(clip.scalars_props, "invert")
        
        if lock_clip_settings:
            row = layout.row()
            row.label(text="Error: no data available at this time step. Please reload of hit 'preview'.", icon="ERROR")