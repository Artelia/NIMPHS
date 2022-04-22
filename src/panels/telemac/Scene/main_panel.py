# <pep8 compliant>
from bpy.types import Panel, Context


class TBB_PT_TelemacMainPanel(Panel):
    """
    Main panel of the TELEMAC module. This is the 'parent' panel.
    """

    bl_label = "TELEMAC"
    bl_idname = "TBB_PT_TelemacMainPanel"
    bl_parent_id = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        settings = context.scene.tbb_telemac_settings

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
            row.operator("tbb.import_telemac_file", text="Import", icon="IMPORT")
            # row.operator("tbb.reload_telemac_file", text="Reload", icon="FILE_REFRESH")
        else:
            row.operator("tbb.import_telemac_file", text="Import TELEMAC file", icon="IMPORT")
