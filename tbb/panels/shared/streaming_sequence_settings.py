# <pep8 compliant>
from bpy.types import Panel, Context

from tbb.panels.utils import get_selected_object
from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_StreamingSequenceSettingsPanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC 'streaming sequence' settings.
    """
    register_cls = False
    is_custom_base_cls = True

    @classmethod
    def poll(cls, context: Context, module: str) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context
            module (str): name of the module, enum in ['OpenFOAM', 'TELEMAC']

        Returns:
            bool: state
        """

        obj = get_selected_object(context)
        if obj is not None:
            return obj.tbb.is_streaming_sequence and obj.tbb.settings.module == module
        else:
            return False

    def draw(self, sequence_settings: TBB_ModuleStreamingSequenceSettings) -> None:
        """
        Layout of the panel.

        Args:
            sequence_settings (TBB_ModuleStreamingSequenceSettings): 'streaming sequence' settings
        """

        layout = self.layout

        row = layout.row()
        row.prop(sequence_settings, "update", text="Update")
        if sequence_settings.update:
            row = layout.row()
            row.prop(sequence_settings, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(sequence_settings, "anim_length", text="Length")

            row = layout.row()
            row.prop(sequence_settings, "shade_smooth", text="Shade smooth")

            row = layout.row()
            row.prop(sequence_settings, "import_point_data", text="Import point data")

            if sequence_settings.import_point_data:
                row = layout.row()
                row.prop(sequence_settings, "list_point_data", text="List")
