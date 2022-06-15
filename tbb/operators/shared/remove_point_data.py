# <pep8 compliant>
import bpy
from bpy.types import Operator, Context
from bpy.props import StringProperty, EnumProperty

import json
import logging
from tbb.panels.utils import get_selected_object
log = logging.getLogger(__name__)

from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_OT_RemovePointData(Operator):
    """Remove point data from the list to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.remove_point_data"
    bl_label = "Remove point data"
    bl_description = "Remove point data from the list to import as vertex colors"

    var_name: StringProperty(
        name="Variable name",
        description="Name of the variable to remove",
        default="",
    )

    #: bpy.props.EnumProperty: Indicates in which mode to execute this operator. Enum in ['OBJECT', 'OPERATOR'].
    mode: EnumProperty(
        name="Mode",
        description="Indicates in which mode to execute this operator. Enum in ['OBJECT', 'OPERATOR']",
        items=[
            ("OBJECT", "Object", "Execute in object mode"),
            ("OPERATOR", "Operator", "Execute in operator mode"),
        ],
        options={'HIDDEN'},
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

        obj = get_selected_object(context)

        if obj is not None:
            settings = obj.tbb.settings
            point_data = json.loads(settings.point_data)
            index = point_data["names"].index(self.var_name)
            point_data["names"].pop(index)
            point_data["units"].pop(index)
            point_data["ranges"].pop(index)
            point_data["types"].pop(index)
            point_data["dimensions"].pop(index)
            obj.tbb.settings.point_data = json.dumps(point_data)
        else:
            log.warning(f"Object with name {self.obj_name} does not exist.")
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'FINISHED'}
