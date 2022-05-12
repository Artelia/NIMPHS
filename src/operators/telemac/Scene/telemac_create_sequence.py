# <pep8 compliant>
import bpy
from bpy.types import Context, Event

import time

from src.operators.utils import get_collection
from src.operators.utils import get_object_dimensions_from_mesh
from src.operators.shared.create_sequence import TBB_CreateSequence
from src.operators.telemac.utils import run_on_step_create_mesh_sequence_telemac


class TBB_OT_TelemacCreateSequence(TBB_CreateSequence):
    """
    Create an OpenFOAM sequence using the settings defined in the
    main panel of the module and the 'create sequence' panel.
    """
    register_cls = True
    is_custom_base_cls = True

    bl_idname = "tbb.telemac_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator. Calls 'super().poll(...)'.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context.scene.tbb.settings.telemac, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Calls 'super().execute(...)'.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        return super().execute(context.scene.tbb.settings.telemac, context, 'TELEMAC')

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'Create TELEMAC Mesh sequence' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event.type == "ESC":
            super().stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_point <= self.end_time_point:
                try:
                    start = time.time()
                    run_on_step_create_mesh_sequence_telemac(context, self.current_frame, self.current_time_point,
                                                             self.start_time_point, self.user_sequence_name)
                    el_time = "{:.4f}".format(time.time() - start)  # el_time = elapsed time
                    print("CreateSequence::TELEMAC: " + el_time + "s, time_point = " + str(self.current_time_point))
                except Exception as error:
                    print("ERROR::TBB_OT_OpenfoamCreateSequence: " + str(error))
                    self.report({"ERROR"}, "An error occurred creating the sequence, (time_step = " +
                                str(self.current_time_point) + ")")
                    super().stop(context)
                    return {"CANCELLED"}

            else:
                super().stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            # Update the progress bar
            context.scene.tbb.progress_value = self.current_time_point / (self.end_time_point - self.start_time_point)
            context.scene.tbb.progress_value *= 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}
