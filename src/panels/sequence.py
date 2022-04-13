from bpy.types import Panel

class TBB_PT_Sequence(Panel):
    bl_label = "Toolsbox blender sequence"
    bl_idname = "TBB_PT_Sequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj.tbb_sequence.is_tbb_sequence

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        tbb_sequence = obj.tbb_sequence

        row = layout.row()
        row.prop(tbb_sequence, "update_on_frame_change", text="Update")
        if tbb_sequence.update_on_frame_change:
            row = layout.row()
            row.prop(tbb_sequence, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(tbb_sequence, "anim_length", text="Length")

            row = layout.row()
            row.prop(tbb_sequence, "import_point_data", text="Import point data")

            if tbb_sequence.import_point_data:
                row = layout.row()
                row.prop(tbb_sequence, "list_point_data", text="List")