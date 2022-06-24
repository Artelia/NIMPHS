# <pep8 compliant>
from bpy.types import Context, Timer
from bpy.props import EnumProperty, StringProperty


class TBB_ModalOperator():
    """Base class of TBB modal operators."""

    register_cls = False
    is_custom_base_cls = True

    # -------------------------------- #
    # /!\ For testing purpose only /!\ #
    # -------------------------------- #
    #: bpy.props.StringProperty: Use this property to pass data as a JSON stringified block of data.
    test_data: StringProperty(
        name="Test data",
        description="Use this property to pass data as a JSON stringified block of data",
        default=""
    )

    #: bpy.props.EnumProperty: Indicate which mode to use for this operator. Enum in ['MODAL', 'TEST'].
    mode: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['MODAL', 'TEST']",
        items=[
            ('MODAL', "Modal", "Run modal"),  # noqa: F821
            ('TEST', "Test", "Run for unit tests"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.types.Timer: Timer which triggers the 'modal' method of operators
    timer: Timer = None

    def prepare(self, context: Context, label: str, step: float = 1e-6) -> None:
        """
        Prepare the execution of the modal operator.

        Args:
            context (Context): context
            label (str): label to display on the progress bar
            step (float, optional): time_step value for the timer. Defaults to 1e-6.
        """

        # Create timer event
        wm = context.window_manager
        self.timer = wm.event_timer_add(time_step=step, window=context.window)
        wm.modal_handler_add(self)

        # Setup prograss bar
        context.scene.tbb.m_op_label = label
        context.scene.tbb.m_op_value = -1.0

        context.scene.tbb.m_op_running = True

    def update_progress(self, context: Context, step: int, end: int) -> None:
        """
        Update progress bar value.

        Args:
            context (Context): context
            step (int): current step in the process
            end (int): ending point of the process
        """

        context.scene.tbb.m_op_value = (step / end) * 100

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
        context.scene.tbb.m_op_value = -1.0

        # Reset operator variables information
        context.scene.tbb.op_vars.clear()

        if cancelled:
            self.report({'INFO'}, "Create sequence cancelled")
