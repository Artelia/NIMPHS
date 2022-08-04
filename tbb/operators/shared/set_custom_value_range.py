# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty, FloatProperty

import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.properties.shared.file_data import TBB_FileData
from tbb.properties.utils.point_data import PointDataInformation


class TBB_OT_SetCustomValueRange(Operator):
    """Set custom point data value range."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.set_custom_value_range"
    bl_label = "Set custom value range"
    bl_description = "Set custom point data value range"

    #: bpy.props.EnumProperty: Indicate the activator of this operator. Enum in ['OBJECT', 'OPERATOR'].
    source: EnumProperty(
        name="Source",  # noqa: F821
        description="Indicate the activator of this operator.",
        items=[
            ("OBJECT", "Object", "Execute in object mode"),  # noqa: F821
            ("OPERATOR", "Operator", "Execute in operator mode"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa: F821
    )

    #: bpy.props.StringProperty: JSON stringified PointDataInformation of the selected point data.
    chosen: StringProperty(
        name="Chosen",
        description="JSON stringified PointDataInformation of the selected point data",
        default="",
        options={'HIDDEN'},  # noqa: F821
    )

    min: FloatProperty(
        name="Minimum",
        description="Set minimum input value",
        default=0.0,
        precision=6
    )

    max: FloatProperty(
        name="Maximum",
        description="Set maximum input value",
        default=1.0,
        precision=6
    )

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Popup window to let the user edit the value range of the selected point data.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        data = PointDataInformation(json_string=self.chosen).range
        self.min = data.minC
        self.max = data.maxC

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            _context (Context): context
        """

        row = self.layout.row()
        row.prop(self, "min", text="Minimum")

        row = self.layout.row()
        row.prop(self, "max", text="Maximum")

    def execute(self, context: Context) -> set:
        """
        Edit new selected values for the chosen point data.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Get file data
        if self.source == 'OBJECT':

            obj = get_selected_object(context)
            if obj is None:
                self.report({'WARNING'}, "No selected object")
                log.error("No selected object.", exc_info=1)
                return {'CANCELLED'}

            file_data: TBB_FileData = context.scene.tbb.file_data.get(obj.tbb.uid, None)

        if self.source == 'OPERATOR':

            file_data: TBB_FileData = context.scene.tbb.file_data.get("ops", None)

        # Update value range of selected point data
        chosen = PointDataInformation(json_string=self.chosen)
        chosen.range.minC = self.min
        chosen.range.maxC = self.max
        file_data.vars.update(chosen)

        # Update operator list of chosen point data
        if self.source == 'OPERATOR':
            context.scene.tbb.op_vars.update(chosen)

        if context.area is not None:
            context.area.tag_redraw()

        return {'FINISHED'}
