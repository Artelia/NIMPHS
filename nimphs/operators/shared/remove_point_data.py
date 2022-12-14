# <pep8 compliant>
from bpy.types import Operator, Context
from bpy.props import StringProperty, EnumProperty

import logging
log = logging.getLogger(__name__)

from nimphs.panels.utils import get_selected_object
from nimphs.properties.utils.point_data import PointDataManager


class NIMPHS_OT_RemovePointData(Operator):
    """Remove point data from the list to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.remove_point_data"
    bl_label = "Remove point data"
    bl_description = "Remove point data from the list to import as vertex colors"

    #: bpy.props.StringProperty: Name of the variable to remove.
    var_name: StringProperty(
        name="Variable name",
        description="Name of the variable to remove",
        default="",
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

    def execute(self, context: Context) -> set:
        """
        Remove point data from the list using the given name.

        Args:
            context (Context): context
            name (str): name of point data

        Returns:
            set: state of the operator
        """

        # Get point data
        if self.source == 'OBJECT':
            obj = get_selected_object(context)
            if obj is None:
                log.warning("No selected object.", exc_info=1)
                return {'CANCELLED'}

            point_data = obj.nimphs.settings.point_data.list
            data = PointDataManager(point_data)

        if self.source == 'OPERATOR':
            data = context.scene.nimphs.op_vars

        # Remove selected point data from the list
        data.remove(data.names.index(self.var_name))

        # Save the new list of chosen point data
        if self.source == 'OBJECT':
            obj.nimphs.settings.point_data.list = data.dumps()
        if self.source == 'OPERATOR':
            context.scene.nimphs.op_vars = data

        if context.area is not None:
            context.area.tag_redraw()

        return {'FINISHED'}
