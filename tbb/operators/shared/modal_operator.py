# <pep8 compliant>
from bpy.props import EnumProperty
from bpy.types import Context, Timer


class TBB_ModalOperator():
    """Base class of TBB modal operators."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.props.EnumProperty: Indicate whether the operator should run modal or normal. Enum in ['MODAL', 'NORMAL'].
    mode: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicate whether the operator should run modal or normal. Enum in ['MODAL', 'NORMAL']",
        items=[
            ('MODAL', "Modal", "TODO"),  # noqa: F821
            ('NORMAL', "Normal", "TODO"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.types.Timer: Timer which triggers the 'modal' method of operators
    timer: Timer = None

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Stop the 'create sequence' process. Used for both modules.

        Args:
            context (Context): context
            cancelled (bool, optional): ask to report 'create sequence cancelled'. Defaults to False.
        """

        # Reset timer if it was running modal
        if self.timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)
            self.timer = None

        context.scene.tbb.m_op_running = False
        context.scene.tbb.progress_value = -1.0

        # Reset operator variables information
        context.scene.tbb.op_vars.clear()

        if cancelled:
            self.report({'INFO'}, "Create sequence cancelled")
