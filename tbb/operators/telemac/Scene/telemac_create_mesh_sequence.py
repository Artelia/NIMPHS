# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import time
import logging
log = logging.getLogger(__name__)

from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings
from tbb.panels.utils import get_selected_object
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData


class TBB_OT_TelemacCreateMeshSequence(TBB_CreateMeshSequence):
    """Create a TELEMAC 'mesh sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.telemac_create_mesh_sequence"
    bl_label = "Create mesh sequence"
    bl_description = "Create a 'mesh sequence' using the selected parameters. Press 'esc' to cancel"

    #: TBB_TelemacImportSettings: import settings
    import_settings: PointerProperty(type=TBB_TelemacImportSettings)

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

        return obj.tbb.module == 'TELEMAC'

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Prepare operators settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        # Load temporary data
        context.scene.tbb.tmp_data["ops"] = TBB_TelemacTemporaryData(self.obj.tbb.settings.file_path, False)
        self.max_length = context.scene.tbb.tmp_data["ops"].nb_time_points

        # Used in tests
        if self.mode == 'NORMAL':
            return {'FINISHED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window of the operator.

        Args:
            context (Context): context
        """

        # Import settings
        box = self.layout.box()
        box.label(text="Import")
        row = box.row()
        row.prop(self.import_settings, "compute_value_ranges", text="Compute value ranges")

        super().draw(context)

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the 'create_mesh_sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operation, enum in ['PASS_THROUGH', 'CANCELLED']
        """

        from tbb.operators.telemac.utils import run_one_step_create_mesh_sequence_telemac

        start = time.time()

        try:
            run_one_step_create_mesh_sequence_telemac(context, self)
        except Exception:
            log.error(f"Error generating mesh sequence at time point '{self.time_point}'", exc_info=1)
            self.report({'ERROR'}, "An error occurred creating the sequence")
            super().stop(context)
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        return {'PASS_THROUGH'}
