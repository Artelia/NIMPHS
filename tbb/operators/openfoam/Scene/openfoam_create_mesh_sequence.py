# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import time
import logging
from tbb.properties.openfoam.openfoam_clip import TBB_OpenfoamClipProperty
from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)

from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from tbb.operators.shared.create_mesh_sequence import TBB_CreateMeshSequence
from tbb.panels.utils import get_selected_object
from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings


class TBB_OT_OpenfoamCreateMeshSequence(TBB_CreateMeshSequence):
    """Create an OpenFOAM 'mesh sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_mesh_sequence"
    bl_label = "Create mesh sequence"
    bl_description = "Create mesh a sequence using the selected parameters. Press 'esc' to cancel"
    bl_options = {'REGISTER', 'UNDO'}

    #: TBB_OpenfoamImportSettings: import settings
    import_settings: PointerProperty(type=TBB_OpenfoamImportSettings)

    #: TBB_OpenfoamImportSettings: clip settings
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)

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
        from tbb.operators.openfoam.utils import load_openfoam_file

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        # Load file data
        succeed, file_reader = load_openfoam_file(self.obj.tbb.settings.file_path,
                                                  case_type=self.import_settings.case_type,
                                                  decompose_polyhedra=self.import_settings.decompose_polyhedra)
        if not succeed:
            log.critical(f"Unable to open file '{self.obj.tbb.settings.file_path}'")
            return {'CANCELLED'}

        context.scene.tbb.tmp_data["ops"] = TBB_OpenfoamTemporaryData(file_reader)

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: Context) -> None:
        """
        UI layout of the popup window of the operator.

        Args:
            context (Context): context
        """

        layout = self.layout

        # Import settings
        box = layout.box()
        box.label(text="Import")
        row = box.row()
        row.prop(self.import_settings, "decompose_polyhedra", text="Decompose polyhedra")
        row = box.row()
        row.prop(self.import_settings, "triangulate", text="Triangulate")
        row = box.row()
        row.prop(self.import_settings, "case_type", text="Case")

        # Clip settings
        box = layout.box()
        box.label(text="Clip")
        row = box.row()
        row.prop(self.clip, "type", text="Type")

        if self.clip.type == 'SCALAR':

            if self.clip.scalar.name != 'NONE':
                row = box.row()
                row.prop(self.clip.scalar, "name")

                row = box.row()

                var_type = VariablesInformation(self.clip.scalar.name).get(0, prop='TYPE')

                if var_type == 'VECTOR':
                    row.prop(self.clip.scalar, "vector_value", text="Value")
                else:
                    row.prop(self.clip.scalar, "value", text="Value")

                row = box.row()
                row.prop(self.clip.scalar, "invert")
            else:
                row = box.row()
                row.label(text="No data available.", icon='ERROR')

        super().draw(context)

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the 'create_mesh_sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operation, enum in ['PASS_THROUGH', 'CANCELLED']
        """

        from tbb.operators.openfoam.utils import run_one_step_create_mesh_sequence_openfoam
        start = time.time()

        try:
            run_one_step_create_mesh_sequence_openfoam(context, self)
        except Exception:
            log.critical(f"Error generating mesh sequence at time point '{self.time_point}'", exc_info=1)
            self.report({'ERROR'}, "An error occurred creating the sequence")
            super().stop(context)
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        return {'PASS_THROUGH'}
