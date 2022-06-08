# <pep8 compliant>
from bpy.types import Context

from tbb.panels.utils import lock_create_operator
from tbb.panels.shared.create_sequence import TBB_CreateSequencePanel


class TBB_PT_OpenfoamCreateSequence(TBB_CreateSequencePanel):
    """UI panel to manage the creation of new OpenFOAM sequences."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "Create sequence"
    bl_idname = "TBB_PT_OpenfoamCreateSequence"
    bl_parent_id = "TBB_PT_OpenfoamMainPanel"
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

        return super().poll(context.scene.tbb.settings.openfoam.tmp_data, context)

    def draw(self, context: Context) -> None:
        """
        Layout of the panel. Calls parent draw function.

        Args:
            context (Context): context
        """

        settings = context.scene.tbb.settings.openfoam
        enable_rows = super().draw(settings, context)
        lock_operator, err_message = lock_create_operator(settings)

        layout = self.layout
        layout.row().separator()

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_name", text="Name")

        row = layout.row()
        row.enabled = not lock_operator
        row.operator("tbb.openfoam_create_sequence", text="Create sequence", icon='RENDER_ANIMATION')

        # Lock the create_sequence operator if the sequence name is already taken or empty
        if lock_operator:
            row = layout.row()
            row.label(text=err_message, icon='ERROR')
