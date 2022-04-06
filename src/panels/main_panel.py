from bpy.types import Panel

class TBB_PT_MainPanel(Panel):
    bl_label = "Toolsbox blender"
    bl_idname = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolsbox blender"

    # Data used for the preview
    file_reader = None
    openfoam_data = None
    openfoam_mesh = None

    def draw(self, context):
        layout = self.layout

        # Get settings
        try:
            settings = context.scene.tbb_settings[0]
        except IndexError as error:
            settings = None

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

        # Preview section
        if settings != None:
            row = layout.row()
            row.label(text="Preview")
            row = layout.row()
            row.prop(settings, "preview_time_step")
            row = layout.row()
            row.operator("tbb.preview", text="Preview", icon="HIDE_OFF")