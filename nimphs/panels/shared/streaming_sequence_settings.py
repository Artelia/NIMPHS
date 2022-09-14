# <pep8 compliant>
from bpy.types import Panel, Context, Object

from nimphs.panels.utils import draw_point_data, get_selected_object
from nimphs.properties.shared.module_streaming_sequence_settings import NIMPHS_ModuleStreamingSequenceSettings


class NIMPHS_StreamingSequenceSettingsPanel(Panel):
    """Base UI panel for 'streaming sequence' settings."""

    register_cls = False
    is_custom_base_cls = True

    @classmethod
    def poll(cls, context: Context, module: str) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context
            module (str): name of the module. Enum in ['OpenFOAM', 'TELEMAC'].

        Returns:
            bool: state
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.nimphs.is_streaming_sequence and obj.nimphs.module == module
        else:
            return False

    def draw(self, context: Context, obj: Object, sequence: NIMPHS_ModuleStreamingSequenceSettings) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
            obj (Object): sequence object
            sequence (NIMPHS_ModuleStreamingSequenceSettings): sequence settings
        """

        file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)

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

        # Sequence settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Sequence")

        row = box.row()
        row.prop(sequence, "start", text="Start")
        row = box.row()
        row.prop(sequence, "length", text="Length")
        row = box.row()
        row.prop(sequence, "shade_smooth", text="Shade smooth")
