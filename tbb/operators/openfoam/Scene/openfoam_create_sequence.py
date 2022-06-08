# <pep8 compliant>
from bpy.types import Context, Event

import time

from tbb.operators.shared.create_sequence import TBB_CreateSequence
from tbb.operators.openfoam.utils import run_one_step_create_mesh_sequence_openfoam


class TBB_OT_OpenfoamCreateSequence(TBB_CreateSequence):
    """
    Create an OpenFOAM sequence using the settings defined in the
    main panel of the module and the 'create sequence' panel.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a sequence using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator. Calls 'super().poll(...)'.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context.scene.tbb.settings.openfoam, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Calls 'super().execute(...)'.
        If mode is set to 'NORMAL', run the operator without using the modal method (locks blender UI).

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        running_mode = super().execute(context.scene.tbb.settings.openfoam, context, 'OpenFOAM')
        if running_mode == {'RUNNING_MODAL'}:
            return running_mode

        for time_point in range(self.start_time_point, self.end_time_point, 1):
            state = self.run_one_step(context, time_point)
            if state != {'PASS'}:
                super().stop(context)
                return state

        super().stop(context)
        return {'FINISHED'}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the OpenFOAM 'create mesh sequence' process.

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
            if self.current_time_point <= self.end_time_point:
                state = self.run_one_step(context, self.current_time_point)
                if state != {'PASS'}:
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Create sequence finished")
                return {'FINISHED'}

            # Update the progress bar
            context.scene.tbb.progress_value = self.current_time_point / (self.end_time_point - self.start_time_point)
            context.scene.tbb.progress_value *= 100
            self.current_time_point += 1
            self.current_frame += 1

        return {'PASS_THROUGH'}

    def run_one_step(self, context: Context, time_point: int) -> set:
        """
        Run one step of the create mesh sequence process.

        Args:
            context (Context): context
            time_point (int): time point to generate

        Returns:
            set: state of the operation, enum in ['PASS', 'CANCELLED']
        """

        try:
            start = time.time()
            run_one_step_create_mesh_sequence_openfoam(context, self.current_frame, time_point,
                                                       self.start_time_point, self.user_sequence_name)
            el_time = "{:.4f}".format(time.time() - start)  # el_time = elapsed time
            print("CreateSequence::OpenFOAM: " + el_time + "s, time_point = " + str(time_point))
        except Exception as error:
            print("ERROR::TBB_OT_OpenfoamCreateSequence: " + str(error))
            self.report({'ERROR'}, "An error occurred creating the sequence, (time_step = " + str(time_point) + ")")
            super().stop(context)
            return {'CANCELLED'}

        return {'PASS'}
