# <pep8 compliant>
import bpy
from bpy.types import Context, Event

import time

from ...shared.create_sequence import TBB_CreateSequence
from ...utils import get_collection


class TBB_OT_TelemacCreateSequence(TBB_CreateSequence):
    """
    Create an OpenFOAM sequence using the settings defined in the
    main panel of the module and the 'create sequence' panel.
    """

    bl_idname = "tbb.telemac_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator. Calls 'super().poll(...)'.

        :type context: Context
        :rtype: bool
        """

        return super().poll(context.scene.tbb_settings.telemac, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Calls 'super().execute(...)'.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        return super().execute(context.scene.tbb_settings.telemac, context, 'TELEMAC')

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'Create TELEMAC Mesh sequence' process.

        :type context: Context
        :type event: Event
        :return: state of the operator
        :rtype: set
        """

        if event.type == "ESC":
            super().stop(context, cancelled=True)
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
                    super().stop(context)
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
                super().stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            context.scene.tbb_progress_value = self.current_time_point / \
                (self.end_time_point - self.start_time_point) * 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}
