# <pep8 compliant>
from bpy.types import Panel, Context

from tbb.panels.utils import get_selected_object


class TBB_PT_TelemacMeshSequence(Panel):
    """UI panel for TELEMAC 'mesh sequence' settings."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC Mesh sequence"
    bl_idname = "TBB_PT_TelemacMeshSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.tbb.is_mesh_sequence
        else:
            return False

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        layout = self.layout

        obj = get_selected_object(context)
        if obj is not None:
            settings = obj.tbb.settings

            row = layout.row()
            row.prop(settings, "import_point_data", text="Import point data")

            if settings.import_point_data:
                row = layout.row()
                row.prop(settings, "point_data", text="List")
