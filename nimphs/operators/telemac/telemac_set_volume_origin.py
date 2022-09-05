# <pep8 compliant>
from bpy.types import Operator, Context, Event, Object

import logging
log = logging.getLogger(__name__)

import numpy as np

from nimphs.panels.utils import get_selected_object


class NIMPHS_OT_TelemacSetVolumeOrigin(Operator):
    """Operator to set origin of a volume to a TELEMAC 3D model."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.set_volume_origin"
    bl_label = "Set volume origin"
    bl_description = "Set origin of volume to TELEMAC 3D model (align origins)"

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
        context.scene.nimphs.op_target = None

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: Context) -> set:
        """
        Align origins of volume and TELEMAC 3D model.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        target = context.scene.nimphs.op_target

        if target is None:
            self.report({'WARNING'}, "Selected target is None")
            return {'CANCELLED'}

        # Check that the selected target is either a plane or the parent object of a TELEMAC object
        parent = target.parent
        is_plane = parent is not None and parent.type == 'EMPTY' and parent.nimphs.module == 'TELEMAC'
        is_parent = target.type == 'EMPTY' and target.nimphs.module == 'TELEMAC'

        if not (is_plane or is_parent):
            self.report({'WARNING'}, "The selected target is not a TELEMAC object")
            return {'CANCELLED'}

        # Set location of selected volume object to computed origin
        self.obj.location = self.origin

        model = parent if is_plane else target
        file_data = context.scene.nimphs.file_data.get(model.nimphs.uid, None)

        # Resize volume to fit model's dimensions
        self.obj.dimensions = file_data.dimensions

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
        row.prop_search(context.scene.nimphs, "op_target", context.scene, "objects", text="Target")

        # Get file data of target
        target = context.scene.nimphs.op_target
        if target is None:
            return

        if target.parent is not None and target.parent.type == 'EMPTY' and target.parent.nimphs.module == 'TELEMAC':
            # If a child object is selected (plane of TELEMAC 3D)
            file_data = context.scene.nimphs.file_data.get(target.parent.nimphs.uid, None)
        elif target.nimphs.module == 'TELEMAC':
            # If the parent object is selected
            file_data = context.scene.nimphs.file_data.get(target.nimphs.uid, None)
        else:
            return

        if file_data is not None:
            row = box.row()
            self.origin = (np.min(file_data.vertices[:, 0]), np.min(file_data.vertices[:, 1]), 0)
            row.label(text=f"Origin: {self.origin}")
