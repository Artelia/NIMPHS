# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import time
import logging
log = logging.getLogger(__name__)

from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.operators.openfoam.utils import load_openfoam_file, run_one_step_create_mesh_sequence_openfoam
from tbb.panels.utils import get_selected_object
from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings


class TBB_OT_OpenfoamCreateMeshSequence(TBB_CreateMeshSequence):
    """Create an OpenFOAM 'mesh sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_mesh_sequence"
    bl_label = "Create mesh sequence"
    bl_description = "Create mesh a sequence using the selected parameters. Press 'esc' to cancel"

    #: TBB_OpenfoamImportSettings: import settings
    import_settings: PointerProperty(type=TBB_OpenfoamImportSettings)

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
        Prepare operators settings.
        Function triggered before the user can edit settings.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def draw(self, _context: Context) -> None:
        """
        UI layout of the popup window of the operator.

        Args:
            context (Context): context
        """

        layout = self.layout

        box = layout.box()
        box.label(text="Import")
        row = box.row()
        row.prop(self.import_settings, "decompose_polyhedra", text="Decompose polyhedra")
        row = box.row()
        row.prop(self.import_settings, "triangulate", text="Triangulate")
        row = box.row()
        row.prop(self.import_settings, "case_type", text="Case")

        box = layout.box()
        box.label(text="Sequence")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "end", text="End")
        row = box.row()
        row.prop(self, "name", text="Name")

    def execute(self, context: Context) -> set:
        """
        Call parent execute function.

        If mode is set to 'NORMAL', run the operator without using the modal method (locks blender UI).

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Load file data
        succeed, file_reader = load_openfoam_file(self.obj.tbb.settings.file_path,
                                                  case_type=self.import_settings.case_type,
                                                  decompose_polyhedra=self.import_settings.decompose_polyhedra)
        if not succeed:
            log.critical(f"Unable to open file '{self.obj.tbb.settings.file_path}'")
            return {'CANCELLED'}

        self.tmp_data = TBB_OpenfoamTemporaryData(file_reader)

        return super().execute(context)

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the OpenFOAM 'create mesh sequence' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event.type == 'ESC':
            super().stop(context, cancelled=True)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.time_point <= self.end:
                state = self.run_one_step(context)
                if state != {'PASS_THROUGH'}:
                    return state

            else:
                super().stop(context)
                self.report({'INFO'}, "Create sequence finished")
                return {'FINISHED'}

            # Update the progress bar
            context.scene.tbb.progress_value = self.time_point / (self.end - self.start)
            context.scene.tbb.progress_value *= 100
            self.time_point += 1
            self.frame += 1

        return {'PASS_THROUGH'}

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the 'create_mesh_sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operation, enum in ['PASS_THROUGH', 'CANCELLED']
        """

        start = time.time()

        try:
            run_one_step_create_mesh_sequence_openfoam(context, self.tmp_data, self.frame,
                                                       self.time_point, self.start, self.name)
        except Exception:
            log.critical(f"Error generating mesh sequence at time point '{self.time_point}'", exc_info=1)
            self.report({'ERROR'}, "An error occurred creating the sequence")
            super().stop(context)
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        return {'PASS_THROUGH'}
