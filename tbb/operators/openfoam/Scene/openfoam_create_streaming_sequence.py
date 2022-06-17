# <pep8 compliant>
from bpy.types import Context, Event

import logging
from tbb.operators.openfoam.utils import generate_openfoam_streaming_sequence_obj
log = logging.getLogger(__name__)

from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from tbb.operators.shared.create_streaming_sequence import TBB_CreateStreamingSequence
from tbb.panels.utils import get_selected_object


class TBB_OT_OpenfoamCreateStreamingSequence(TBB_CreateStreamingSequence):
    """Create an OpenFOAM 'streaming sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_streaming_sequence"
    bl_label = "Create streaming sequence"
    bl_description = "Create a 'streaming sequence' using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        if super().poll(context):
            obj = get_selected_object(context)
        else:
            return False

        return obj.tbb.module == 'OpenFOAM'

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operators settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """
        from tbb.operators.openfoam.utils import load_openfoam_file

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        # Load file data
        succeed, file_reader = load_openfoam_file(self.obj.tbb.settings.file_path)
        if not succeed:
            log.critical(f"Unable to open file '{self.obj.tbb.settings.file_path}'")
            return {'CANCELLED'}

        context.scene.tbb.tmp_data["ops"] = TBB_OpenfoamTemporaryData(file_reader)
        self.max_length = context.scene.tbb.tmp_data["ops"].nb_time_points

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window of the operator.

        Args:
            context (Context): context
        """

        super().draw(context)

    def execute(self, context: Context) -> set:
        """
        Generate the 'streaming sequence' object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        obj = generate_openfoam_streaming_sequence_obj(context, self.obj, self.name)
        obj.tbb.settings.openfoam.s_sequence.shade_smooth = self.shade_smooth
        return super().execute(context, obj)
