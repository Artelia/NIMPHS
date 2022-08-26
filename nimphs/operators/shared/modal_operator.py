# <pep8 compliant>
from bpy.types import Context, Timer
from bpy.props import EnumProperty, StringProperty


class NIMPHS_ModalOperator():
    """Base class of NIMPHS modal operators."""

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
        name="Mode",                                    # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['MODAL', 'TEST']",
        items=[
            ('MODAL', "Modal", "Run modal"),            # noqa: F821
            ('TEST', "Test", "Run for unit tests"),     # noqa: F821
        ],
        options={'HIDDEN'},                             # noqa: F821
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
        context.scene.nimphs.m_op_label = label
        context.scene.nimphs.m_op_value = -1.0

        context.scene.nimphs.m_op_running = True

    def update_progress(self, context: Context, step: int, end: int) -> None:
        """
        Update progress bar value.

        Args:
            context (Context): context
            step (int): current step in the process
            end (int): ending point of the process
        """

        context.scene.nimphs.m_op_value = (step / end) * 100

    def set_progress(self, context: Context, value: float) -> None:
        """
        Set custom value of progress bar.

        Args:
            context (Context): context
            value (float): new value to display
        """

        context.scene.nimphs.m_op_value = value

    def update_label(self, context: Context, label: str) -> None:
        """
        Update label of progress bar.

        Args:
            context (Context): context
            label (str): new label to display
        """

        context.scene.nimphs.m_op_label = label

    def stop(self, context: Context, canceled: bool = False) -> None:
        """
        Stop the 'create sequence' process. Used for both modules.

        Args:
            context (Context): context
            canceled (bool, optional): ask to report 'create sequence canceled'. Defaults to False.
        """

        # Reset timer if it was running modal
        if self.timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)
            self.timer = None

        context.scene.nimphs.m_op_running = False
        context.scene.nimphs.m_op_value = -1.0

        # Reset operator variables information
        context.scene.nimphs.op_vars.clear()

        if canceled:
            self.report({'INFO'}, "Create sequence canceled")
