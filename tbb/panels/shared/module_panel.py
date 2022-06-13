# <pep8 compliant>
from bpy.types import Panel, Context, Object

from typing import Union

from tbb.panels.utils import get_selected_object
from tbb.operators.utils import get_temporary_data


class TBB_ModulePanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC modules.

    Specific settings are added in the classes which derive from this one.
    """

    register_cls = False
    is_custom_base_cls = True

    def draw(self, context: Context) -> tuple[bool, Union[Object, None]]:
        """
        Layout of the panel.

        Args:
            context (Context): context

        Returns:
            tuple[bool, Union[Object, None]]: enable rows, selected object
        """

        obj = get_selected_object(context)
        # If the object is None or is not a TELEMAC or OpenFOAM file
        if obj is None or obj.tbb.module not in ['TELEMAC', 'OpenFOAM']:
            return False, None

        layout = self.layout

        # If the object is a sequence (streaming or mesh)
        if obj.tbb.is_streaming_sequence or obj.tbb.is_mesh_sequence:
            row = layout.row()
            row.label(text="Sequence: see Object Properties.", icon='INFO')
            return False, None

        # Display file_path information
        box = layout.box()
        row = box.row()
        row.label(text=f"File: {obj.tbb.settings.file_path}")
        row.operator("tbb.edit_file_path", text="", icon="GREASEPENCIL")

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb.create_sequence_is_running

        tmp_data = get_temporary_data(obj)
        module = obj.tbb.module
        # Check temporary data
        if tmp_data is None or not tmp_data.is_ok():
            row = layout.row()
            row.enabled = enable_rows
            row.label(text="Reload data: ", icon='ERROR')
            row.operator("tbb.reload_" + module.lower() + "_file", text="Reload", icon='FILE_REFRESH')
            return False, None

        return enable_rows, obj
