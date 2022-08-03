# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.properties.utils.point_data import PointDataManager
from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings


class TBB_OT_TelemacCreateMeshSequence(TBB_CreateMeshSequence):
    """Operator to create a TELEMAC 'mesh sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_create_mesh_sequence"
    bl_label = "Mesh sequence"
    bl_description = "Create a 'mesh sequence'. Press 'esc' to cancel"

    #: TBB_TelemacImportSettings: import settings
    import_settings: PointerProperty(type=TBB_TelemacImportSettings)

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

        return obj.tbb.module == 'TELEMAC'

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operator settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        if context.scene.tbb.file_data.get(self.obj.tbb.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # Clear selected point data
        context.scene.tbb.op_vars.clear()
        # "Copy" file data
        context.scene.tbb.file_data["ops"] = context.scene.tbb.file_data[self.obj.tbb.uid]
        self.max = context.scene.tbb.file_data["ops"].nb_time_points - 1

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            import json

            data = json.loads(self.test_data)

            self.end = data["end"]
            self.start = data["start"]
            self.time_point = self.start
            self.point_data.list = self.test_data
            self.point_data.import_data = PointDataManager(data["vars"]).length() > 0

            return {'FINISHED'}
        else:
            # Do not change the name if the operator runs in 'TEST' mode
            self.name = "Mesh_sequence"

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window.

        Args:
            context (Context): context
        """

        super().draw(context)

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the 'create mesh sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operation. Enum in ['PASS_THROUGH', 'CANCELLED'].
        """

        from tbb.operators.utils.object import TelemacObjectUtils

        start = time.time()

        try:
            TelemacObjectUtils.step_create_mesh_sequence(context, self)
        except Exception:
            log.error(f"Error generating mesh sequence at time point '{self.time_point}'", exc_info=1)
            self.report({'ERROR'}, "An error occurred creating the sequence")
            super().stop(context)
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        return {'PASS_THROUGH'}