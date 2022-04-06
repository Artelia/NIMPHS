from bpy.types import Panel

class TBB_PT_MainPanel(Panel):
    bl_label = "Toolsbox blender"
    bl_idname = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolsbox blender"

    file_reader = None

    def draw(self, context):
        layout = self.layout

        # Get settings
        settings = None
        if len(context.scene.tbb_settings) > 0:
            settings = context.scene.tbb_settings[0]

        row = layout.row()
        row.label(text="Import")
        
        # Import section
        row = layout.row()
        if settings != None and settings.file_path != "":
            box = row.box()
            box.label(text="File: " + settings.file_path)
            row = layout.row()
            row.operator("tbb.import_foam_file", text="Import", icon="IMPORT")
            row.operator("tbb.reload_foam_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.operator("tbb.import_foam_file", text="Import OpenFoam file", icon="IMPORT")