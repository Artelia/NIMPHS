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

        # Check if we need to lock the ui
        enable_rows = not settings.create_sequence_is_running

        row = layout.row()
        row.label(text="Import")
        
        # Import section
        row = layout.row()
        if settings.file_path != "":
            box = row.box()
            box.label(text="File: " + settings.file_path)
            row = layout.row()
            row.enabled = enable_rows
            row.operator("tbb.import_foam_file", text="Import", icon="IMPORT")
            row.operator("tbb.reload_foam_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.operator("tbb.import_foam_file", text="Import OpenFoam file", icon="IMPORT")

        obj = context.active_object
        # Even if no objects are selected, the last selected object remains in the active_objects variable
        if len(context.selected_objects) == 0:
            obj = None
            
        if obj == None or not obj.tbb_openfoam_sequence.is_on_frame_change_sequence:

            if context.scene.tbb_temp_data.is_ok():
                # Preview section
                row = layout.row()
                row.enabled = enable_rows
                row.label(text="Preview")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, '["preview_time_step"]', text="Time step")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, "preview_point_data", text="Points")
                row = layout.row()
                row.enabled = enable_rows
                row.operator("tbb.preview", text="Preview", icon="HIDE_OFF")
            
            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            elif settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")

        else:
            row = layout.row()
            row.label(text="Edit settings of this sequence in the object properties panel", icon="INFO")
            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            if not context.scene.tbb_temp_data.is_ok() and settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")