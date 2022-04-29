# <pep8 compliant>
from bpy.types import Context

from ...create_sequence import CreateSequencePanel
from ...utils import lock_create_operator


class TBB_PT_TelemacCreateSequence(CreateSequencePanel):
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
        If false, hides the panel.

        :type context: Context
        :rtype: bool
        """

        return CreateSequencePanel.poll(context.scene.tbb_telemac_tmp_data, context)

    def draw(self, context: Context):
        """
        Layout of the panel.

        :type context: Context
        """

        settings = context.scene.tbb_telemac_settings
        enable_rows = CreateSequencePanel.draw(self, settings, context)
        lock, message = lock_create_operator(settings)

        layout = self.layout

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "normalize_sequence_obj", text="Normalize")

        layout.row().separator()

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_name", text="Name")

        row = layout.row()
        row.enabled = lock
        row.operator("tbb.telemac_create_sequence", text="Create sequence", icon="RENDER_ANIMATION")

        # Lock the create_sequence operator if the sequence name is already taken or empty
        if lock:
            row = layout.row()
            row.label(text=message, icon="ERROR")
