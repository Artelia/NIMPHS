# <pep8 compliant>
import bpy
from bpy.types import Operator, Context, RenderSettings

from ..utils import setup_streaming_sequence_object


class CreateSequence(Operator):
    """
    Create a sequence using the settings defined in the main panel and the 'create sequence' panel.
    """

    def __init__(self) -> None:
        super().__init__()
        self.timer = None
        self.sequence_name = ""
        self.user_sequence_name = ""
        self.start_time_point = 0
        self.end_time_point = 0
        self.current_time_point = 0
        self.current_frame = 0
        self.chrono_start = 0

    @classmethod
    def poll(self, settings, context: Context) -> bool:
        """
        Common poll method for OpenFOAM and TELEMAC 'Create sequence' operators.

        :param settings: settings
        :type context: Context
        :rtype: bool
        """

        if settings.sequence_type == "mesh_sequence":
            return not context.scene.tbb_create_sequence_is_running and settings["start_time_point"] < settings["end_time_point"]
        elif settings.sequence_type == "streaming_sequence":
            return not context.scene.tbb_create_sequence_is_running
        else:  # Lock ui by default
            return False

    def execute(self, settings, context: Context, type: str) -> set:
        """
        Common execute method for OpenFOAM and TELEMAC 'Create sequence' operators.

        :param operator: target operator
        :param settings: scene settings
        :type context: Context
        :param type: module name, enum in ['OpenFOAM', 'TELEMAC']
        :type type: str
        :return: state of the operator
        :rtype: set
        """

        wm = context.window_manager

        if settings.sequence_type == "mesh_sequence":
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

        elif settings.sequence_type == "streaming_sequence":
            # Warn the user when the selected start frame may be weird
            if settings.frame_start < context.scene.frame_start or settings.frame_start > context.scene.frame_end:
                self.report({"WARNING"}, "Frame start is not in the selected time frame.")

            obj_name = settings.sequence_name + "_sequence"
            blender_mesh = bpy.data.meshes.new(name=settings.sequence_name + "_mesh")
            obj = bpy.data.objects.new(obj_name, blender_mesh)
            setup_streaming_sequence_object(obj, context, type)

            context.collection.objects.link(obj)

            # As mentionned here, lock the interface because the custom handler will alter data on frame change
            # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
            RenderSettings.use_lock_interface = True

            self.report({"INFO"}, "Sequence successfully created")

            return {"FINISHED"}

        else:
            self.report({"ERROR"}, "Unknown sequence type (type = " + str(settings.sequence_type) + ")")
            return {"FINISHED"}

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Common stop function for OpenFOAM and TELEMAC 'Create sequence' operators.

        :param operator: operator to stop
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
