# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import VIEW3D_HT_tool_header

import logging
log = logging.getLogger(__name__)

from nimphs.properties.shared.nimphs_scene import NIMPHS_Scene


@persistent
def nimphs_on_save_pre(_dummy) -> None:
    """Save data before the blender file is saved."""

    for obj in bpy.data.objects:
        file_data = bpy.context.scene.nimphs.file_data.get(obj.nimphs.uid, None)
        if file_data is not None:
            obj.nimphs.settings.point_data.save = file_data.vars.dumps()


# Inspired by: https://blog.michelanders.nl/2017/04/how-to-add-progress-indicator-to-the-info-header-in-blender.html
def register_custom_progress_bar() -> None:
    """Register the custom progress bar."""

    # Save the original draw method of Info header
    if not NIMPHS_Scene.view_3d_ht_tool_header_draw_saved:
        NIMPHS_Scene.view_3d_ht_tool_header_draw = VIEW3D_HT_tool_header.draw
        NIMPHS_Scene.view_3d_ht_tool_header_draw_saved = True

    # Create a new draw function
    def new_info_header_draw(self, context):
        # First call to the original function
        NIMPHS_Scene.view_3d_ht_tool_header_draw(self, context)

        # Then add the prop that acts as a progress bar
        scene_prop = context.scene.get("nimphs", None)
        if scene_prop is None:
            return

        m_op_value = context.scene.nimphs.get("m_op_value", -1)
        if m_op_value >= 0.0 and m_op_value <= 100.0:
            self.layout.separator()
            text = context.scene.nimphs.m_op_label
            self.layout.prop(context.scene.nimphs, "m_op_value", text=text, slider=True)

    # Replace the draw function by our new function
    VIEW3D_HT_tool_header.draw = new_info_header_draw
