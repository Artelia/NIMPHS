# <pep8 compliant>
import bpy
from bpy.types import Operator, Context, Event

from ...utils import get_collection, poll_create_sequence

import time


class TBB_OT_TelemacCreateSequence(Operator):
    """
    Create a sequence using the settings defined in the main panel and the 'create sequence' panel.
    """

    bl_idname = "tbb.telemac_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    timer = None
    sequence_object_name = ""
    user_sequence_name = ""
    start_time_point = 0
    current_time_point = 0
    end_time_point = 0
    current_frame = 0

    chrono_start = 0

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

        :type context: Context
        :rtype: bool
        """

        settings = context.scene.tbb_telemac_settings
        return poll_create_sequence(settings, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        wm = context.window_manager
        settings = context.scene.tbb_telemac_settings
        tmp_data = context.scene.tbb_telemac_tmp_data

        # Create timer event
        self.timer = wm.event_timer_add(time_step=1e-3, window=context.window)
        wm.modal_handler_add(self)

        # Setup prograss bar
        context.scene.tbb_progress_label = "Create sequence"
        context.scene.tbb_progress_value = -1.0

        # Setup for creating the sequence
        self.start_time_point = settings["start_time_point"]
        self.current_time_point = settings["start_time_point"]
        self.end_time_point = settings["end_time_point"]
        self.current_frame = context.scene.frame_current
        self.user_sequence_name = settings.sequence_name

        context.scene.tbb_create_sequence_is_running = True

        return {"RUNNING_MODAL"}

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'Create sequence' process.

        :type context: Context
        :type event: Event
        :return: state of the operator
        :rtype: set
        """

        if event.type == "ESC":
            self.stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_point <= self.end_time_point:
                self.chrono_start = time.time()
                try:
                    mesh = None
                except Exception as error:
                    print("ERROR::TBB_OT_TelemacCreateSequence: " + str(error))
                    self.report({"ERROR"}, "An error occurred creating the sequence, (time_step = " +
                                str(self.current_time_point) + ")")
                    self.stop(context)
                    return {"CANCELLED"}

                # First time point, create the sequence object
                if self.current_time_point == self.start_time_point:
                    # Create the blender object (which will contain the sequence)
                    obj = bpy.data.objects.new(self.user_sequence_name + "_sequence", mesh)
                    self.sequence_object_name = obj.name
                    get_collection("TBB_TELEMAC", context).objects.link(obj)
                else:
                    pass

                print("CreateSequence::TELEMAC: " + "{:.4f}".format(time.time() - self.chrono_start) + "s, time_point = "
                      + str(self.current_time_point))

            else:
                self.stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            context.scene.tbb_progress_value = self.current_time_point / \
                (self.end_time_point - self.start_time_point) * 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Stop the 'Create sequence' process.

        :type context: Context
        :param cancelled: ask to report 'Create sequence cancelled', defaults to False
        :type cancelled: bool, optional
        """

        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        self.timer = None
        context.scene.tbb_create_sequence_is_running = False
        context.scene.tbb_progress_value = -1.0
        if cancelled:
            self.report({"INFO"}, "Create sequence cancelled")
