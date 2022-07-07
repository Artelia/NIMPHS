# <pep8 compliant>
from bpy.props import IntProperty
from bpy.types import Event, Context

import logging
log = logging.getLogger(__name__)

from tbb.operators.shared.utils import update_end
from tbb.operators.shared.modal_operator import TBB_ModalOperator
from tbb.operators.shared.create_sequence import TBB_CreateSequence


class TBB_CreateMeshSequence(TBB_CreateSequence, TBB_ModalOperator):
    """Operator to create mesh sequences used in both modules."""

    register_cls = False
    is_custom_base_cls = True

    #: int: Time point currently processed when creating a sequence
    time_point: int = 0

    #: int: Current frame during the 'create sequence' process (different from time point)
    frame: int = 0

    #: bpy.props.IntProperty: Ending point of the sequence.
    end: IntProperty(
        name="End",  # noqa F821
        description="Ending point of the sequence",
        default=1,
        update=update_end,
        soft_min=0,
        min=0
    )

    def invoke(self, _context: Context, _event: Event) -> set:
        """
        Prepare operators settings. Function triggered before the user can edit settings.\
        This method has to be overloaded in derived classes.

        Args:
            _context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        return {'RUNNING_MODAL'}

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        super().draw(context)

        # Sequence settings
        box = self.layout.box()
        box.label(text="Sequence")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "end", text="End")
        row = box.row()
        row.prop(self, "name", text="Name")

    def execute(self, context: Context) -> set:
        """
        Prepare the execution of the 'create mesh sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Copy data from temporary variables information
        self.point_data.list = context.scene.tbb.op_vars.dumps()

        # Load data for the create sequence process
        self.frame = context.scene.frame_current
        self.time_point = self.start

        if self.mode == 'MODAL':
            super().prepare(context, "Generating sequence...")
            return {'RUNNING_MODAL'}

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        elif self.mode == 'TEST':
            self.invoke(context, None)

            while self.time_point < self.end:
                self.run_one_step(context)
                self.time_point += 1
                self.frame += 1

            return {'FINISHED'}

        else:
            log.warning(f"Undefined operator mode '{self.mode}'. Running modal by default.", exc_info=1)
            super().prepare(context, "Generating sequence...")
            return {'RUNNING_MODAL'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'create_mesh_sequence' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event.type == 'ESC':
            super().stop(context, canceled=True)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.time_point <= self.end:
                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    super().stop(context)
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Create sequence finished")
                return {'FINISHED'}

            # Update the progress bar
            context.scene.tbb.m_op_value = (self.time_point / (self.end - self.start)) * 100
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}

    def run_one_step(self, _context: Context) -> set:
        """
        Run one step of the 'create mesh sequence' process.

        Args:
            _context (Context): context

        Returns:
            set: state of the operation. Enum in ['PASS_THROUGH', 'CANCELLED'].
        """

        return {'PASS_THROUGH'}
