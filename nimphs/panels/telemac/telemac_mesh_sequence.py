# <pep8 compliant>
from bpy.types import Panel, Context

from nimphs.panels.utils import draw_point_data, get_selected_object


class NIMPHS_PT_TelemacMeshSequence(Panel):
    """UI panel for TELEMAC 'mesh sequence' settings."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "TELEMAC Mesh sequence"
    bl_idname = "NIMPHS_PT_TelemacMeshSequence"
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
            return obj.nimphs.is_mesh_sequence
        else:
            return False

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        if obj is not None:

            # Display file_path information
            box = self.layout.box()
            row = box.row()
            row.label(text=f"File: {obj.nimphs.settings.file_path}")
            row.operator("nimphs.edit_file_path", text="", icon="GREASEPENCIL")

            try:
                file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)
            except KeyError:
                file_data = None

            # Check file data
            if file_data is None or not file_data.is_ok():
                row = self.layout.row()
                row.label(text="Reload data: ", icon='ERROR')
                row.operator("nimphs.reload_telemac_file", text="Reload", icon='FILE_REFRESH')
                return

            # Point data settings
            point_data = obj.nimphs.settings.point_data

            box = self.layout.box()
            row = box.row()
            row.label(text="Point data")
            row = box.row()
            row.prop(point_data, "import_data", text="Import point data")

            if point_data.import_data and file_data is not None:

                draw_point_data(box, point_data, show_range=True, edit=True)

                row = box.row()
                op = row.operator("nimphs.add_point_data", text="Add", icon='ADD')
                op.available = file_data.vars.dumps()
                op.chosen = point_data.list
                op.source = 'OBJECT'
