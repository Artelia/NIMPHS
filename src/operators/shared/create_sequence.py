# <pep8 compliant>
from bpy.types import Operator, Context, RenderSettings

from src.properties.openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings
from src.properties.telemac.Scene.telemac_settings import TBB_TelemacSettings
from src.operators.openfoam.utils import generate_openfoam_streaming_sequence_obj
from src.operators.telemac.utils import generate_telemac_streaming_sequence_obj
from src.operators.utils import setup_streaming_sequence_object


class TBB_CreateSequence(Operator):
    """
    Base class of the 'CreateSequence' operators.
    """
    register_cls = False
    is_custom_base_cls = True

    #: bpy.types.Timer: Timer which triggers the 'modal' method of operators
    timer = None
    #: str: Name of the sequence object
    sequence_name = ""
    #: str: Sequence name typed by the user
    user_sequence_name = ""
    #: int: Starting point of the sequence to generate
    start_time_point = 0
    #: int: Ending point of the sequence to generate
    end_time_point = 0
    #: int: Time point currently processed when creating a sequence
    current_time_point = 0
    #: int: Current frame during the 'create sequence' process (different from time point)
    current_frame = 0
    #: float: Variable used to measure execution times of the operators
    chrono_start = 0

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
        If false, locks the UI button of the operator.

        :param settings: settings
        :type context: Context
        :rtype: bool
        """

        tbb_csir = context.scene.tbb.create_sequence_is_running  # csir = create sequence is running
        if settings.sequence_type == "mesh_sequence":
            return not tbb_csir and settings["start_time_point"] < settings["end_time_point"]
        elif settings.sequence_type == "streaming_sequence":
            return not tbb_csir
        else:  # Lock ui by default
            return False

    def execute(self, settings: TBB_OpenfoamSettings | TBB_TelemacSettings, context: Context, module: str) -> set:
        """
        Main method of the operator.

        :param operator: target operator
        :param settings: scene settings
        :type settings: TBB_OpenfoamSettings | TBB_TelemacSettings
        :type context: Context
        :param module: module name, enum in ['OpenFOAM', 'TELEMAC']
        :type module: str
        :return: state of the operator
        :rtype: set
        """

        wm = context.window_manager

        if settings.sequence_type == "mesh_sequence":
            # Create timer event
            self.timer = wm.event_timer_add(time_step=1e-6, window=context.window)
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

            context.scene.tbb.create_sequence_is_running = True

            return {"RUNNING_MODAL"}

        elif settings.sequence_type == "streaming_sequence":
            # Warn the user when the selected start frame may be weird
            if settings.frame_start < context.scene.frame_start or settings.frame_start > context.scene.frame_end:
                self.report({"WARNING"}, "Frame start is not in the selected time frame.")

            if module == 'OpenFOAM':
                obj = generate_openfoam_streaming_sequence_obj(context, settings.sequence_name)
                seq_settings = obj.tbb.settings.openfoam.streaming_sequence
            if module == 'TELEMAC':
                obj = generate_telemac_streaming_sequence_obj(context, settings.sequence_name)
                seq_settings = obj.tbb.settings.telemac.streaming_sequence

            setup_streaming_sequence_object(obj, seq_settings, settings.tmp_data.nb_time_points, settings, module)

            context.scene.collection.objects.link(obj)

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
        context.scene.tbb.create_sequence_is_running = False
        context.scene.tbb_progress_value = -1.0
        if cancelled:
            self.report({"INFO"}, "Create sequence cancelled")
