# <pep8 compliant>
from bpy.types import Context

from ...shared.create_sequence import TBB_CreateSequencePanel
from ...utils import lock_create_operator


class TBB_PT_OpenfoamCreateSequence(TBB_CreateSequencePanel):
    """
    UI panel to manage the creation of new sequences.
    """

    bl_label = "Create sequence"
    bl_idname = "TBB_PT_OpenfoamCreateSequence"
    bl_parent_id = "TBB_PT_OpenfoamMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        return TBB_CreateSequencePanel.poll(context.scene.tbb_openfoam_tmp_data, context)

    def draw(self, context: Context):
        """
        Layout of the panel.

        :type context: Context
        """

        settings = context.scene.tbb_openfoam_settings
        enable_rows = TBB_CreateSequencePanel.draw(self, settings, context)
        lock_operator, err_message = lock_create_operator(settings)

        layout = self.layout
        layout.row().separator()

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_name", text="Name")

        row = layout.row()
        row.enabled = not lock_operator
        row.operator("tbb.openfoam_create_sequence", text="Create sequence", icon="RENDER_ANIMATION")

        # Lock the create_sequence operator if the sequence name is already taken or empty
        if lock_operator:
            row = layout.row()
            row.label(text=err_message, icon="ERROR")
