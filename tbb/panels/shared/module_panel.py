# <pep8 compliant>
from bpy.types import Panel, Context, Object

from typing import Union

from tbb.panels.utils import get_selected_object


class TBB_ModulePanel(Panel):
    """
    Base UI panel for OpenFOAM and TELEMAC modules.

    Specific settings are added in the classes which derive from this one.
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
        if obj is None or obj.tbb.module not in ['TELEMAC', 'OpenFOAM'] or obj.tbb.module != module:
            return False, False, None

        # If the object is a sequence (streaming or mesh)
        if obj.tbb.is_streaming_sequence or obj.tbb.is_mesh_sequence:
            row = self.layout.row()
            row.label(text="Sequence: see Object Properties.", icon='INFO')
            return False, False, obj

        # Display file_path information
        box = self.layout.box()
        row = box.row()
        row.label(text=f"File: {obj.tbb.settings.file_path}")
        row.operator("tbb.edit_file_path", text="", icon="GREASEPENCIL")

        # Check if we need to lock the ui
        enable_rows = not context.scene.tbb.create_sequence_is_running

        tmp_data = context.scene.tbb.tmp_data.get(obj.tbb.uid, None)

        module = obj.tbb.module
        # Check temporary data
        if tmp_data is None or not tmp_data.is_ok():
            row = self.layout.row()
            row.enabled = enable_rows
            row.label(text="Reload data: ", icon='ERROR')
            row.operator("tbb.reload_" + module.lower() + "_file", text="Reload", icon='FILE_REFRESH')
            return False, False, obj

        return enable_rows, True, obj
