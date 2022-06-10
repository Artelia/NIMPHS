# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import json
import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.operators.utils import get_sequence_settings
from tbb.operators.telemac.utils import get_streaming_sequence_temporary_data


class TBB_OT_AddPointData(Operator):
    """Add point data to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.add_point_data"
    bl_label = "Add point data"
    bl_description = "Add point data to import as vertex colors"

    def point_data_items(self, _context: Context) -> list:
        """
        Format point data to present to the user.

        Args:
            _context (Context): context

        Returns:
            list: point data
        """

        items = []
        if self.available_point_data != "":
            data = json.loads(self.available_point_data)
            for name, unit in zip(data["names"], data["units"]):
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

    def invoke(self, context: Context, event: Event) -> set:
        """
        Let the user choose the point data to add.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        obj = get_selected_object(context)

        # TODO: use this for both modules
        if obj.tbb.settings.module == 'TELEMAC':
            tmp_data = get_streaming_sequence_temporary_data(obj)
            self.available_point_data = json.dumps(tmp_data.vars_info)
        else:
            log.warning("Not implemented yet for other modules.")
            return {'CANCELLED'}

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

        obj = get_selected_object(context)
        sequence = get_sequence_settings(obj)

        # TODO: use this for both modules
        if obj.tbb.settings.module == 'TELEMAC':
            point_data = json.loads(sequence.point_data)

            selected_point_data = json.loads(self.point_data)
            point_data["names"].append(selected_point_data["name"])
            point_data["units"].append(selected_point_data["unit"])
            point_data["ranges"].append(None)

            sequence.point_data = json.dumps(point_data)
        else:
            log.warning("Not implemented yet for other modules.")
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'FINISHED'}
