from bpy.types import Panel

class TBB_PT_MainPanel(Panel):
    bl_label = "Toolsbox blender"
    bl_idname = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolsbox blender"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tbb_settings

        row = layout.row()
        row.label(text="Import")
        
        # Import section
        row = layout.row()
        if settings.file_path != "":
            box = row.box()
            box.label(text="File: " + settings.file_path)
            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.operator("tbb.import_foam_file", text="Import", icon="IMPORT")
            row.operator("tbb.reload_foam_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.operator("tbb.import_foam_file", text="Import OpenFoam file", icon="IMPORT")

        if context.scene.tbb_temp_data.is_ok():
            # Preview section
            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.label(text="Preview")
            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.prop(settings, '["preview_time_step"]', text="Time step")
            row = layout.row()
            row.enabled = not settings.create_sequence_is_running
            row.operator("tbb.preview", text="Preview", icon="HIDE_OFF")
        
        else:
            row = layout.row()
            row.label(text="Error: please reload the file.", icon="ERROR")