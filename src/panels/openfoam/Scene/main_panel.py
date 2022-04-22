# <pep8 compliant>
from bpy.types import Panel, Context


class TBB_PT_OpenfoamMainPanel(Panel):
    """
    Main panel of the OpenFOAM module. This is the 'parent' panel.
    """

    bl_label = "OpenFOAM"
    bl_idname = "TBB_PT_OpenfoamMainPanel"
    bl_parent_id = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        settings = context.scene.tbb_openfoam_settings

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
            row.operator("tbb.import_openfoam_file", text="Import", icon="IMPORT")
            row.operator("tbb.reload_openfoam_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.operator("tbb.import_openfoam_file", text="Import OpenFOAM file", icon="IMPORT")

        obj = context.active_object
        # Even if no objects are selected, the last selected object remains in the active_objects variable
        if len(context.selected_objects) == 0:
            obj = None

        if obj is None or not obj.tbb_openfoam_sequence.is_streaming_sequence:

            if context.scene.tbb_openfoam_tmp_data.is_ok():
                # Preview section
                row = layout.row()
                row.enabled = enable_rows
                row.label(text="Preview")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, '["preview_time_point"]', text="Time step")
                row = layout.row()
                row.enabled = enable_rows
                row.prop(settings, "preview_point_data", text="Points")
                row = layout.row()
                row.enabled = enable_rows
                row.operator("tbb.openfoam_preview", text="Preview", icon="HIDE_OFF")

            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            elif settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")

        else:
            row = layout.row()
            row.label(text="Edit settings of this sequence in the object properties panel", icon="INFO")
            # If the file_path is not empty, it means that there is an error with temp data. Need to reload.
            if not context.scene.tbb_openfoam_tmp_data.is_ok() and settings.file_path != "":
                row = layout.row()
                row.label(text="Error: please reload the file.", icon="ERROR")
