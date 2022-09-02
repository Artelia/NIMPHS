# <pep8 compliant>
from bpy.types import Context, Event
from bpy.props import PointerProperty

import logging
log = logging.getLogger(__name__)

import time

from nimphs.panels.utils import get_selected_object
from nimphs.panels.openfoam.utils import draw_clip_settings
from nimphs.properties.utils.point_data import PointDataManager
from nimphs.properties.openfoam.clip import NIMPHS_OpenfoamClipProperty
from nimphs.operators.shared.create_mesh_sequence import NIMPHS_CreateMeshSequence
from nimphs.properties.openfoam.import_settings import NIMPHS_OpenfoamImportSettings


class NIMPHS_OT_OpenfoamCreateMeshSequence(NIMPHS_CreateMeshSequence):
    """Create an OpenFOAM 'mesh sequence'."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.openfoam_create_mesh_sequence"
    bl_label = "Mesh sequence"
    bl_description = "Create mesh a sequence. Press 'esc' to cancel"

    #: NIMPHS_OpenfoamImportSettings: import settings
    import_settings: PointerProperty(type=NIMPHS_OpenfoamImportSettings)

    #: NIMPHS_OpenfoamImportSettings: clip settings
    clip: PointerProperty(type=NIMPHS_OpenfoamClipProperty)

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

        return obj.nimphs.module == 'OpenFOAM'

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

        if context.scene.nimphs.file_data.get(self.obj.nimphs.uid, None) is None:
            self.report({'ERROR'}, "Reload file data first")
            return {'CANCELLED'}

        # Clear selected point data
        context.scene.nimphs.op_vars.clear()
        # "Copy" file data information
        self.import_settings.skip_zero_time = self.obj.nimphs.settings.openfoam.import_settings.skip_zero_time
        context.scene.nimphs.file_data["ops"] = context.scene.nimphs.file_data[self.obj.nimphs.uid]
        self.max = context.scene.nimphs.file_data["ops"].nb_time_points - 1

        # -------------------------------- #
        # /!\ For testing purpose only /!\ #
        # -------------------------------- #
        if self.mode == 'TEST':
            import json

            data = json.loads(self.test_data)

            self.time_point = data["start"]
            self.start = data["start"]
            self.end = data["end"]
            self.point_data.list = data["vars"]
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

        # Import settings
        box = self.layout.box()
        box.label(text="Import")
        row = box.row()
        row.prop(self.import_settings, "decompose_polyhedra", text="Decompose polyhedra")
        row = box.row()
        row.prop(self.import_settings, "skip_zero_time", text="Skip zero time")
        row = box.row()
        row.prop(self.import_settings, "triangulate", text="Triangulate")
        row = box.row()
        row.prop(self.import_settings, "case_type", text="Case")

        # Clip settings
        draw_clip_settings(self.layout, self.clip)

        super().draw(context)

    def run_one_step(self, context: Context) -> set:
        """
        Run one step of the 'create mesh sequence' process.

        Args:
            context (Context): context

        Returns:
            set: state of the operator. Enum in ['PASS_THROUGH', 'CANCELLED'].
        """

        from nimphs.operators.utils.object import OpenfoamObjectUtils
        start = time.time()

        try:
            OpenfoamObjectUtils.step_create_mesh_sequence(context, self)
        except Exception:
            log.critical(f"Error at time point {self.time_point}, frame {self.frame}", exc_info=1)
            self.report({'ERROR'}, "An error occurred creating the sequence")
            super().stop(context)
            return {'CANCELLED'}

        log.info("{:.4f}".format(time.time() - start) + "s")
        return {'PASS_THROUGH'}
