# <pep8 compliant>
from bpy.types import Operator, Context, Event
from bpy.props import EnumProperty

from tbb.panels.utils import get_selected_object


class TBB_OT_AddPointData(Operator):
    """Add point data to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.add_point_data"
    bl_label = "Add point data"
    bl_description = "Add point data to import as vertex colors"

    point_data: EnumProperty(
        name="Point data",
        description="Point data to import as vertex colors",
        items=[
            ("NONE", "None", "None"),
        ]
    )

    def invoke(self, context: Context, event: Event) -> set:
        obj = get_selected_object(context)
        seq_settings = obj
