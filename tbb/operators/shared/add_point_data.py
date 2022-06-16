# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty, StringProperty

import logging
from tbb.panels.utils import get_selected_object
log = logging.getLogger(__name__)

from tbb.properties.utils import VariablesInformation


class TBB_OT_AddPointData(Operator):
    """Add point data to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.add_point_data"
    bl_label = "Add point data"
    bl_description = "Add point data to import as vertex colors"
    bl_options = {'REGISTER', 'UNDO'}

    def point_data_items(self, _context: Context) -> list:
        """
        Format point data to present to the user.

        Args:
            _context (Context): context

        Returns:
            list: point data
        """

        items = []
        vars_info = VariablesInformation(self.available)

        identifier = VariablesInformation()
        for name, unit, id in zip(vars_info.names, vars_info.units, range(vars_info.length())):
            identifier.append(data=vars_info.get(id))
            items.append((identifier.dumps(), (name + ", (" + unit + ")") if unit != "" else name, "Undocumented"))
            identifier.clear()

        return items

    #: bpy.props.EnumProperty: Point data to import as vertex colors.
    point_data: EnumProperty(
        name="Point data",
        description="Point data to import as vertex colors",
        items=point_data_items,
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.props.StringProperty: JSON stringified list of available point data.
    available: StringProperty(
        name="Available point data",
        description="JSON stringified list of available point data",
        default="",
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.props.StringProperty: JSON stringified list of chosen point data.
    chosen: StringProperty(
        name="Available point data",
        description="JSON stringified list of chosen point data",
        default="",
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.props.EnumProperty: Indicates the activator of this operator. Enum in ['OBJECT', 'OPERATOR'].
    source: EnumProperty(
        name="Source",  # noqa F821
        description="Indicates the activator of this operator.\
Enum in ['OBJECT', 'OPERATOR/OpenFOAM', 'OPERATOR/TELEMAC']",
        items=[
            ("OBJECT", "Object", "Execute in object mode"),  # noqa F821
            ("OPERATOR/OpenFOAM", "Operator (OpenFOAM)", "Execute in operator mode, OpenFOAM module"),  # noqa F821
            ("OPERATOR/TELEMAC", "Operator (TELEMAC)", "Execute in operator mode, TELEMAC module"),  # noqa F821
        ],
        options={'HIDDEN'},  # noqa F821
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

        chosen = VariablesInformation(self.chosen)
        available = VariablesInformation(self.available)

        # Remove already chosen variables from the list of available point data
        to_present = VariablesInformation()
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

        # Get point data
        if self.source == 'OBJECT':
            obj = get_selected_object(context)
            if obj is None:
                log.warning("No selected object.", exc_info=1)
                return {'CANCELLED'}

            point_data = obj.tbb.settings.point_data.list

        if self.source == 'OPERATOR':
            # TODO: I think we can find a better solution to get access to these data.
            import bpy
            point_data = bpy.types.TBB_OT_openfoam_create_mesh_sequence.list
        if self.source == 'OPERATOR/TELEMAC':
            # TODO: I think we can find a better solution to get access to these data.
            import bpy
            point_data = bpy.types.TBB_OT_openfoam_create_mesh_sequence.list

        # Add selected point data to the list
        add = VariablesInformation(self.point_data)
        data = VariablesInformation(point_data)
        data.append(data=add.get(0))

        # Save the new list of chosen point data
        if self.source == 'OBJECT':
            obj.tbb.settings.point_data.list = data.dumps()
        if self.source == 'OPERATOR/OpenFOAM':
            bpy.types.TBB_OT_openfoam_create_mesh_sequence.list = data.dumps()
        if self.source == 'OPERATOR/TELEMAC':
            bpy.types.TBB_OT_telemac_create_mesh_sequence.list = data.dumps()

        context.area.tag_redraw()
        return {'FINISHED'}
