# <pep8 compliant>
from bpy.types import Context, Event

import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.operators.openfoam.utils import generate_openfoam_streaming_sequence_obj
from tbb.operators.shared.create_streaming_sequence import TBB_CreateStreamingSequence


class TBB_OT_OpenfoamCreateStreamingSequence(TBB_CreateStreamingSequence):
    """Create an OpenFOAM 'streaming sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_streaming_sequence"
    bl_label = "Streaming sequence"
    bl_description = "Create a 'streaming sequence'."

    @classmethod
    def poll(self, context: Context) -> bool:
        """
        If false, locks the button of the operator.

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
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None:
            return {'CANCELLED'}

        if context.scene.tbb.file_data.get(obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # "Copy" file data information
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[obj.tbb.uid]
        self.max_length = context.scene.tbb.file_data["ops"].nb_time_points

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window.

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

        selected = get_selected_object(context)
        if selected is None:
            return {'CANCELLED'}

        obj = generate_openfoam_streaming_sequence_obj(context, selected, self.name)
        obj.tbb.settings.openfoam.s_sequence.shade_smooth = self.shade_smooth
        return super().execute(context, obj, selected)
