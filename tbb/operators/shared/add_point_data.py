# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import json
import logging
log = logging.getLogger(__name__)
from copy import deepcopy


from tbb.panels.utils import get_selected_object
from tbb.operators.telemac.utils import get_streaming_sequence_temporary_data


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
        obj = get_selected_object(context)

        if self.available_point_data != "":
            if obj.tbb.module == 'TELEMAC':
                data = json.loads(self.available_point_data)
                for name, unit in zip(data["names"], data["units"]):
                    identifier = {"name": name, "unit": unit}
                    ui_name = name + ", (" + unit + ")" if unit != "" else name
                    items.append((json.dumps(identifier), ui_name, "Undocumented"))

            elif obj.tbb.module == 'OpenFOAM':
                return items

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

        if obj.tbb.module == 'TELEMAC':
            tmp_data = get_streaming_sequence_temporary_data(obj)
            available = deepcopy(tmp_data.vars_info)
            to_present = {"names": [], "units": [], "ranges": [], "types": [], "dimensions": []}

            # Remove already chosen variables from the list of available point data
            chosen_point_data = json.loads(obj.tbb.settings.point_data)
            for name, id in zip(available["names"], range(len(available["names"]))):
                if name not in chosen_point_data["names"]:
                    to_present["names"].append(available["names"][id])
                    to_present["units"].append(available["units"][id])
                    to_present["ranges"].append(available["ranges"][id])
                    to_present["types"].append(available["types"][id])
                    to_present["dimensions"].append(available["dimensions"][id])

            self.available_point_data = json.dumps(to_present)

        elif obj.tbb.module == 'OpenFOAM':
            pass

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
        settings = obj.tbb.settings

        # TODO: use this for both modules
        if obj.tbb.module == 'TELEMAC':
            point_data = json.loads(settings.point_data)

            selected_point_data = json.loads(self.point_data)
            point_data["names"].append(selected_point_data["name"])
            point_data["units"].append(selected_point_data["unit"])
            point_data["ranges"].append({"local": {"min": None, "max": None}, "global": {"min": None, "max": None}})
            point_data["types"].append(None)
            point_data["dimensions"].append(None)

            settings.point_data = json.dumps(point_data)
        else:
            log.warning("Not implemented yet for other modules.")
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'FINISHED'}