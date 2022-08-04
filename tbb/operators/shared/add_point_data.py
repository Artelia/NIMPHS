# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.properties.utils.point_data import PointDataManager


class TBB_OT_AddPointData(Operator):
    """Add point data."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.add_point_data"
    bl_label = "Add point data"
    bl_description = "Add point data"

    def point_data_items(self, _context: Context) -> list:
        """
        Format point data to present to the user.

        Args:
            _context (Context): context

        Returns:
            list: point data
        """

        items = []
        vars = PointDataManager(self.available)

        identifier = PointDataManager()
        for name, unit, id in zip(vars.names, vars.units, range(vars.length())):
            identifier.append(data=vars.get(id))
            items.append((identifier.dumps(), (name + ", (" + unit + ")") if unit != "" else name, "Undocumented"))
            identifier.clear()

        items.append(("None", "None", "None"))

        return items

    #: bpy.props.EnumProperty: Point data.
    point_data: EnumProperty(
        name="Point data",
        description="Point data",
        items=point_data_items,
        options={'HIDDEN'},  # noqa: F821
    )

    #: bpy.props.StringProperty: JSON stringified list of available point data.
    available: StringProperty(
        name="Available point data",
        description="JSON stringified list of available point data",
        default="",
        options={'HIDDEN'},  # noqa: F821
    )

    #: bpy.props.StringProperty: JSON stringified list of chosen point data.
    chosen: StringProperty(
        name="Chosen",      # noqa: F821
        description="JSON stringified list of chosen point data",
        default="",
        options={'HIDDEN'},  # noqa: F821
    )

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

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Let the user choose point data to add.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        chosen = PointDataManager(self.chosen)
        available = PointDataManager(self.available)

        # Remove already chosen variables from the list of available point data
        to_present = PointDataManager()
        for name, id in zip(available.names, range(available.length())):
            if name not in chosen.names:
                to_present.append(data=available.get(id))

        self.available = to_present.dumps()

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            _context (Context): context
        """

        row = self.layout.row()
        row.prop(self, "point_data", text="Point data")

    def execute(self, context: Context) -> set:
        """
        Add chosen point data to the list of point data to import.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        if self.point_data == "None":
            return {'CANCELLED'}

        # Get point data
        if self.source == 'OBJECT':
            obj = get_selected_object(context)
            if obj is None:
                self.report({'WARNING'}, "No selected object")
                log.error("No selected object.", exc_info=1)
                return {'CANCELLED'}

            point_data = obj.tbb.settings.point_data.list
            data = PointDataManager(point_data)

        if self.source == 'OPERATOR':
            data = context.scene.tbb.op_vars

        # Add selected point data to the list
        add = PointDataManager(self.point_data)
        data.append(data=add.get(0))

        # Save the new list of chosen point data
        if self.source == 'OBJECT':
            obj.tbb.settings.point_data.list = data.dumps()
        if self.source == 'OPERATOR':
            context.scene.tbb.op_vars = data

        if context.area is not None:
            context.area.tag_redraw()

        return {'FINISHED'}
