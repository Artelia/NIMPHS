# <pep8 compliant>
from bpy.types import Operator, Context, Event, Object

import logging
log = logging.getLogger(__name__)

import numpy as np

from tbb.panels.utils import get_selected_object


class TBB_OT_TelemacSetVolumeOrigin(Operator):
    """Operator to set origin of a volume to a TELEMAC 3D model."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.set_volume_origin"
    bl_label = "Set volume origin"
    bl_description = "Set origin of volume to TELEMAC 3D model (align origins)."

    #: bpy.types.Object: Selected object
    obj: Object = None

    #: tuple[float, float, float]: Computed target origin
    origin: tuple[float, float, float] = (0, 0, 0)

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
            return obj.type == 'VOLUME'
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

        self.obj = get_selected_object(context)
        if self.obj is None:
            return {'CANCELLED'}

        # Set default target object
        context.scene.tbb.op_target = None

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: Context) -> set:
        """
        Align origins of volume and TELEMAC 3D model.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Set location of selected volume object to computed origin
        self.obj.location = self.origin

        return {'FINISHED'}

    def draw(self, context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            context (Context): context
        """

        box = self.layout.box()
        row = box.row()
        row.label(text="Selection")
        row = box.row()
        row.prop_search(context.scene.tbb, "op_target", context.scene, "objects", text="Target")

        # Get file data of target
        target = context.scene.tbb.op_target
        if target is None:
            return

        if target.parent is not None and target.parent.type == 'EMPTY' and target.parent.tbb.module == 'TELEMAC':
            row = box.row()
            row.label(text="Please select parent object.", icon='ERROR')
            return

        file_data = context.scene.tbb.file_data.get(target.tbb.uid, None)

        if file_data is not None:
            row = box.row()
            self.origin = (np.min(file_data.vertices[:, 0]), np.min(file_data.vertices[:, 1]), 0)
            row.label(text=f"Origin: {self.origin}")
