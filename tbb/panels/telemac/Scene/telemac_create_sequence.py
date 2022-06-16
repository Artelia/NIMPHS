# <pep8 compliant>
from bpy.types import Context

from tbb.panels.utils import lock_create_operator
from tbb.panels.shared.create_sequence import TBB_CreateSequencePanel


class TBB_PT_TelemacCreateSequence(TBB_CreateSequencePanel):
    """UI panel to manage the creation of new TELEMAC sequences."""

    register_cls = False
    is_custom_base_cls = False

    bl_label = "Create sequence"
    bl_idname = "TBB_PT_TelemacCreateSequence"
    bl_parent_id = "TBB_PT_TelemacMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel. Calls parent poll function.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context.scene.tbb.settings.telemac.tmp_data, context)

    def draw(self, context: Context):
        """
        Layout of the panel. Calls parent draw function.

        Args:
            context (Context): context
        """

        settings = context.scene.tbb.settings.telemac
        enable_rows = super().draw(settings, context)
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
        row.enabled = not lock
        row.operator("tbb.telemac_create_sequence", text="Create sequence", icon='RENDER_ANIMATION')

        # Lock the create_sequence operator if the sequence name is already taken or empty
        if lock:
            row = layout.row()
            row.label(text=message, icon='ERROR')
