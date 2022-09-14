# <pep8 compliant>
from bpy.types import Panel, Context, Object

from typing import Union

from nimphs.panels.utils import get_selected_object


class NIMPHS_ModulePanel(Panel):
    """
    Base UI panel for all modules.

    Create derived classes to add specific content.
    """

    register_cls = False
    is_custom_base_cls = True

    def draw(self, context: Context, module: str) -> tuple[bool, bool, Union[Object, None]]:
        """
        Layout of the panel.

        Args:
            context (Context): context
            module (str): module name. Enum in ['TELEMAC', 'OpenFOAM'].

        Returns:
            tuple[bool, bool, Union[Object, None]]: enable rows, temp data is available, selected object
        """

        obj = get_selected_object(context)
        # If the object is None or is not a TELEMAC or OpenFOAM file
        if obj is None or obj.nimphs.module not in ['TELEMAC', 'OpenFOAM'] or obj.nimphs.module != module:
            return False, False, None

        # If the object is a sequence (streaming or mesh)
        if obj.nimphs.is_streaming_sequence or obj.nimphs.is_mesh_sequence:
            row = self.layout.row()
            row.label(text="Sequence: see Object Properties.", icon='INFO')
            return False, False, obj

        # Display file_path information
        box = self.layout.box()
        row = box.row()
        row.label(text=f"File: {obj.nimphs.settings.file_path}")
        row.operator("nimphs.edit_file_path", text="", icon="GREASEPENCIL")

        # Check if we need to lock the ui
        enable_rows = not context.scene.nimphs.m_op_running

        file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)

        module = obj.nimphs.module
        # Check file data
        if file_data is None or not file_data.is_ok():
            row = self.layout.row()
            row.enabled = enable_rows
            row.label(text="Reload data: ", icon='ERROR')
            row.operator(f"nimphs.reload_{module.lower()}_file", text="Reload", icon='FILE_REFRESH')
            return False, False, obj

        return enable_rows, True, obj
