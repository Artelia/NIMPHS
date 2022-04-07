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
        return context.scene.tbb_settings.file_path != ""

    def draw(self,context):
        layout = self.layout
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip

        row = layout.row()
        row.prop(clip, "type")