# <pep8 compliant>
from bpy.types import Panel, Context

from ...utils import sequence_name_already_exist


class TBB_PT_TelemacCreateSequence(Panel):
    """
    UI panel to manage the creation of new sequences.
    """

    bl_label = "Create sequence"
    bl_idname = "TBB_PT_TelemacCreateSequence"
    bl_parent_id = "TBB_PT_TelemacMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Determine whether to let the user access the panel or not.

        :type context: Context
        :rtype: bool
        """

        return context.scene.tbb_telemac_tmp_data.is_ok()

    def draw(self, context: Context):
        """
        Layout of the panel.

        :type context: Context
        """

        layout = self.layout
        settings = context.scene.tbb_telemac_settings

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb_create_sequence_is_running
        snae = sequence_name_already_exist(settings.sequence_name)  # snae = sequence_name_already_exist

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, '["start_time_point"]', text="Start")
        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, '["end_time_point"]', text="End")

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "normalize_coordinates_sequence", text="Normalize")
        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "import_point_data")

        if settings.import_point_data:
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "list_point_data", text="List")

        layout.row().separator()
        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_name", text="Name")
        row = layout.row()
        row.enabled = not snae
        row.operator("tbb.telemac_create_sequence", text="Create sequence", icon="RENDER_ANIMATION")

        # Lock the create_sequence operator if the sequence name is already taken
        if snae:
            row = layout.row()
            row.label(text="Sequence name already taken.", icon="ERROR")
