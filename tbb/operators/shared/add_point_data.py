# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import json
import logging

from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)


class TBB_OT_AddPointData(Operator):
    """Add point data to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.add_point_data"
    bl_label = "Add point data"
    bl_description = "Add point data to import as vertex colors"

    def point_data_items(self, context: Context) -> list:
        """
        Format point data to present to the user.

        Args:
            context (Context): context

        Returns:
            list: point data
        """

        items = []
        vars_info = VariablesInformation(self.available_point_data)

        for name, unit in zip(vars_info.names, vars_info.units):
            identifier = {"name": name, "unit": unit}
            ui_name = name + ", (" + unit + ")" if unit != "" else name
            items.append((json.dumps(identifier), ui_name, "Undocumented"))

        return items

    point_data: EnumProperty(
        name="Point data",
        description="Point data to import as vertex colors",
        items=point_data_items
    )

    available_point_data: StringProperty(
        name="Available point data",
        description="JSON stringified list of available point data",
        default=""
    )

    chosen_point_data: StringProperty(
        name="Available point data",
        description="JSON stringified list of chosen point data",
        default=""
    )

    def invoke(self, context: Context, _event: Event) -> set:
        """
        Let the user choose the point data to add.

        Args:
            context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        to_present = VariablesInformation()
        chosen = VariablesInformation(self.chosen_point_data)
        available = VariablesInformation(self.available_point_data)

        # Remove already chosen variables from the list of available point data
        for name, id in zip(available.names, range(available.length())):
            if name not in chosen.names:
                to_present.append(data=available.get(id))

        self.available_point_data = to_present.dumps()
        print(to_present)

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _context: Context) -> None:
        """
        Layout of the popup window.

        Args:
            _context (Context): context
        """

        layout = self.layout

        row = layout.row()
        row.prop(self, "point_data", text="Point data")

    def execute(self, context: Context) -> set:
        """
        Add chosen point data to the list of point data to import.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        try:
            # TODO: I think we can find a better solution to get access to these data.
            import bpy
            point_data = bpy.types.TBB_OT_openfoam_create_mesh_sequence.point_data
        except Exception:
            log.error("No file data available")
            return {'CANCELLED'}

        point_data = VariablesInformation(point_data)
        point_data.append(VariablesInformation(self.point_data).get(0))

        bpy.types.TBB_OT_openfoam_create_mesh_sequence.point_data = point_data.dumps()

        context.area.tag_redraw()
        return {'FINISHED'}
