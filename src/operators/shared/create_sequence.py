# <pep8 compliant>
from bpy.types import Operator, Context, RenderSettings
from bpy.props import StringProperty

from src.operators.utils import setup_streaming_sequence_object
from src.operators.telemac.utils import generate_telemac_streaming_sequence_obj
from src.properties.shared.module_scene_settings import TBB_ModuleSceneSettings
from src.operators.openfoam.utils import generate_openfoam_streaming_sequence_obj


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

    #: bpy.props.StringProperty: Wether the operator should run modal or not, enum in ['MODAL', 'NORMAL']
    mode: StringProperty(
        name="Create sequence mode",
        description="Wether the operator should run modal or not, enum in ['MODAL', 'NORMAL']",
        default="MODAL"
    )

    def __init__(self) -> None:
        super().__init__()
        self.timer = None
        self.sequence_name = ""
        self.user_sequence_name = ""
        self.start_time_point = 0
        self.end_time_point = 0
        self.current_time_point = 0
        self.current_frame = 0

    @classmethod
    def poll(self, settings: TBB_ModuleSceneSettings, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

        Args:
            settings (TBB_ModuleSceneSettings): scene settings
            context (Context): context

        Returns:
            bool: state
        """

        tbb_csir = context.scene.tbb.create_sequence_is_running  # csir = create sequence is running
        if settings.sequence_type == "mesh_sequence":
            return not tbb_csir and settings["start_time_point"] < settings["end_time_point"]
        elif settings.sequence_type == "streaming_sequence":
            return not tbb_csir
        else:  # Lock ui by default
            return False

    def execute(self, settings: TBB_ModuleSceneSettings, context: Context, module: str) -> set:
        """
        Main method of the operator.

        Args:
            settings (TBB_ModuleSceneSettings): scene settings
            context (Context): context
            module (str): name of the module, enum in ['OpenFOAM', 'TELEMAC']

        Returns:
            set: state of the operator
        """

        wm = context.window_manager

        if settings.sequence_type == "mesh_sequence":
            # Create timer event
            self.timer = wm.event_timer_add(time_step=1e-6, window=context.window)
            wm.modal_handler_add(self)

            # Setup prograss bar
            context.scene.tbb.progress_label = "Create sequence"
            context.scene.tbb.progress_value = -1.0

            # Setup for creating the sequence
            self.start_time_point = settings["start_time_point"]
            self.current_time_point = settings["start_time_point"]
            self.end_time_point = settings["end_time_point"]
            self.current_frame = context.scene.frame_current
            self.user_sequence_name = settings.sequence_name

            context.scene.tbb.create_sequence_is_running = True

            if self.mode == 'MODAL':
                return {'RUNNING_MODAL'}
            elif self.mode == 'NORMAL':
                return {'NORMAL'}  # custom value
            else:
                print("WARNING::TBB_CreateSequence: undefined operator mode '" +
                      str(self.mode) + "', running modal by default.")
                return {'RUNNING_MODAL'}

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
        Common stop function for OpenFOAM and TELEMAC 'create sequence' operators.

        Args:
            context (Context): context
            cancelled (bool, optional): ask to report 'create sequence cancelled'. Defaults to False.
        """

        # Reset timer if it was running modal
        if self.timer is not None:
            wm = context.window_manager
            wm.event_timer_remove(self.timer)
            self.timer = None

        context.scene.tbb.create_sequence_is_running = False
        context.scene.tbb.progress_value = -1.0

        if cancelled:
            self.report({"INFO"}, "Create sequence cancelled")
