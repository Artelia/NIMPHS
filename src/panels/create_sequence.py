from bpy.types import Panel

class TBB_PT_CreateSequence(Panel):
    bl_label = "Create sequence"
    bl_idname = "TBB_PT_CreateSequence"
    bl_parent_id = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene.tbb_settings.file_path != ""

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tbb_settings

        if settings.file_path != "":
            row = layout.row()
            row.prop(settings, '["start_time"]', text="Start")
            row = layout.row()
            row.prop(settings, '["end_time"]', text="End")
            row = layout.row()
            row.prop(settings, "import_point_data")