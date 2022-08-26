# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import logging
log = logging.getLogger(__name__)

from nimphs.panels.utils import get_selected_object
from nimphs.operators.utils.object import TelemacObjectUtils
from nimphs.properties.telemac.import_settings import NIMPHS_TelemacImportSettings
from nimphs.operators.shared.create_streaming_sequence import NIMPHS_CreateStreamingSequence


class NIMPHS_OT_TelemacCreateStreamingSequence(NIMPHS_CreateStreamingSequence):
    """Operator to create a TELEMAC 'streaming sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.telemac_create_streaming_sequence"
    bl_label = "Streaming sequence"
    bl_description = "Create a 'streaming sequence'"

    #: NIMPHS_TelemacImportSettings: import settings
    import_settings: PointerProperty(type=NIMPHS_TelemacImportSettings)

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

        return obj.nimphs.module == 'TELEMAC'

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

        if context.scene.nimphs.file_data.get(obj.nimphs.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # Clear selected point data
        context.scene.nimphs.op_vars.clear()
        # "Copy" file data
        context.scene.nimphs.file_data["ops"] = context.scene.nimphs.file_data[obj.nimphs.uid]
        self.max = context.scene.nimphs.file_data["ops"].nb_time_points

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            import json

            data = json.loads(self.test_data)
            self.start = data["start"]
            self.length = data["length"]

            return {'FINISHED'}
        else:
            # Do not change the name if the operator runs in 'TEST' mode
            self.name = "Streaming_sequence"

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

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            self.invoke(context, None)

        obj = TelemacObjectUtils.sequence(context, selected, self.name, self.start)
        obj.nimphs.settings.telemac.s_sequence.shade_smooth = self.shade_smooth
        return super().execute(context, obj, selected)
