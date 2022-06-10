# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import json
import logging
log = logging.getLogger(__name__)

from tbb.panels.utils import get_selected_object
from tbb.operators.utils import get_sequence_settings


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
            for variable in json.loads(self.available_point_data):
                items.append((
                    variable["name"],
                    variable["name"] + ", " + variable["unit"] if variable["unit"] != "" else variable["name"],
                    "Undocumented"
                ))

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
        seq_settings = get_sequence_settings(obj)

        # TODO: use this for both modules
        if obj.tbb.settings.module == 'TELEMAC':
            self.available_point_data = json.dumps(seq_settings.tmp_data.vars_info)
        else:
            log.warning("Not implemented yet for other modules.")
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)
