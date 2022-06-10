# <pep8 compliant>
from bpy.types import Panel, Context, Object

import json

from tbb.panels.utils import get_selected_object
from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_StreamingSequenceSettingsPanel(Panel):
    """Base UI panel for OpenFOAM and TELEMAC 'streaming sequence' settings."""

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
            return obj.tbb.is_streaming_sequence and obj.tbb.module == module
        else:
            return False

    def draw(self, obj: Object, sequence: TBB_ModuleStreamingSequenceSettings) -> None:
        """
        Layout of the panel.

        Args:
            obj (Object): sequence object
            sequence (TBB_ModuleStreamingSequenceSettings): 'streaming sequence' settings
        """

        layout = self.layout
        settings = obj.tbb.settings

        row = layout.row()
        row.prop(sequence, "update", text="Update")
        if sequence.update:
            row = layout.row()
            row.prop(sequence, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(sequence, "anim_length", text="Length")

            row = layout.row()
            row.prop(sequence, "shade_smooth", text="Shade smooth")

            row = layout.row()
            row.prop(settings, "import_point_data", text="Import point data")

            if settings.import_point_data:

                row = layout.row()
                row.prop(settings, "remap_method", text="Method")

                # Display selected point data
                data = json.loads(settings.point_data)
                for name, unit, values in zip(data["names"], data["units"], data["ranges"]):
                    box = layout.box()
                    row = box.row()

                    if values is not None:
                        if settings.remap_method == 'LOCAL':
                            values = "[" + str(values["local"]["min"]) + ";" + str(values["local"]["max"]) + "]"
                        elif settings.remap_method == 'GLOBAL':
                            values = "[" + str(values["global"]["min"]) + ";" + str(values["global"]["max"]) + "]"
                        else:
                            values = "None"
                    else:
                        values = "None"

                    op = row.operator("tbb.remove_point_data", text="", icon='REMOVE')
                    op.obj_name = obj.name_full
                    op.var_name = name
                    row.label(text=name + ", (" + str(unit) + ")" + ",  " + values)

                row = layout.row()
                row.operator("tbb.add_point_data", text="Add", icon='ADD')
