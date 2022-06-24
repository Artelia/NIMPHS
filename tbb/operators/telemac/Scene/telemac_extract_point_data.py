# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings
from tbb.operators.shared.modal_operator import TBB_ModalOperator


class TBB_OT_TelemacExtractPointData(Operator, TBB_ModalOperator):
    """Operator to extract point data from a TELEMAC object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_extract_point_data"
    bl_label = "Extract point data"
    bl_description = "Extract point data from a TELEMAC object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the button of the operator.

        Args:
            context (Context): context

        Returns:
            bool: state of the operator
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.tbb.module == 'TELEMAC'
        else:
            return False

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

        # "Copy" file data
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[obj.tbb.uid]

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        pass

    def execute(self, context: Context) -> set:
        """
        Extract point data.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        pass

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'extract point data' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        pass
