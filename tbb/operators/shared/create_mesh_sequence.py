# <pep8 compliant>
from bpy.types import Event, Context, Object, Timer
from bpy.props import StringProperty, EnumProperty, IntProperty

import time
import logging

from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)
from typing import Union

from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.operators.openfoam.utils import run_one_step_create_mesh_sequence_openfoam
from tbb.operators.telemac.utils import run_one_step_create_mesh_sequence_telemac
from tbb.operators.shared.create_sequence import TBB_CreateSequence
from tbb.panels.utils import get_selected_object


class TBB_CreateMeshSequence(TBB_CreateSequence):
    """Operator to create mesh sequences."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.types.Timer: Timer which triggers the 'modal' method of operators
    timer: Timer = None
    #: str: Name of the sequence object
    obj_name: str = ""
    #: int: Time point currently processed when creating a sequence
    time_point: int = 0
    #: int: Current frame during the 'create sequence' process (different from time point)
    frame: int = 0
    #: int: Module name. Enum in ['OpenFOAM', 'TELEMAC']
    module: str = 'NONE'
    #: bpy.types.Object: Selected object
    obj: Object = None

    #: bpy.props.IntProperty: Starting point of the sequence.
    start: IntProperty(
        name="Start",  # noqa F821
        description="Starting point of the sequence",
        default=0
    )

    #: bpy.props.IntProperty: Ending point of the sequence.
    end: IntProperty(
        name="End",  # noqa F821
        description="Ending point of the sequence",
        default=0
    )

    #: bpy.props.StringProperty: Name to give to the generated sequence object.
    name: StringProperty(
        name="Name",  # noqa F821
        description="Name to give to the generated sequence object",
        default="Mesh"
    )

    def invoke(self, _context: Context, _event: Event) -> set:
        """
        Prepare operators settings.
        Function triggered before the user can edit settings.

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

        layout = self.layout

        # Sequence settings
        box = layout.box()
        box.label(text="Sequence")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "end", text="End")
        row = box.row()
        row.prop(self, "name", text="Name")

    def execute(self, context: Context) -> set:
        """
        Prepare the execution of the 'create_mesh_sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Create timer event
        wm = context.window_manager
        self.timer = wm.event_timer_add(time_step=1e-6, window=context.window)
        wm.modal_handler_add(self)

        # Setup prograss bar
        context.scene.tbb.progress_label = "Create sequence"
        context.scene.tbb.progress_value = -1.0

        # Load data for the create sequence process
        self.frame = context.scene.frame_current
        self.time_point = self.start

        context.scene.tbb.create_sequence_is_running = True

        if self.mode == 'MODAL':
            return {'RUNNING_MODAL'}
        elif self.mode == 'NORMAL':
            return {'NORMAL'}  # custom value to run the process without modal mode (used in tests)
        else:
            log.warning(f"Undefined operator mode '{self.mode}'. Running modal by default.", exc_info=1)
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
            super().stop(context, cancelled=True)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.time_point <= self.end:
                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Create sequence finished")
                return {'FINISHED'}

            # Update the progress bar
            context.scene.tbb.progress_value = self.time_point / (self.end - self.start)
            context.scene.tbb.progress_value *= 100
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}

    def run_one_step(self, _context: Context) -> set:
        """
        Run one step of the 'create_mesh_sequence' process.

        Args:
            _context (Context): context

        Returns:
            set: state of the operation, enum in ['PASS_THROUGH', 'CANCELLED']
        """

        return {'PASS_THROUGH'}
