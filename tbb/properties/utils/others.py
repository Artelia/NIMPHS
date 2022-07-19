# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Context, VIEW3D_HT_tool_header

import logging
log = logging.getLogger(__name__)

DEV_MODE = True


@persistent
def tbb_on_save_pre(_dummy) -> None:
    """
    Save data before the blender file is saved.

    Args:
        scene (Scene): scene
    """

    for obj in bpy.data.objects:
        file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
        if file_data is not None:
            obj.tbb.settings.point_data.save = file_data.vars.dumps()


def update_progress_bar(_self, context: Context) -> None:
    """
    Update function for the custom progress bar. Tag all info areas for redraw.

    Args:
        context (Context): context
    """

    areas = context.window.screen.areas
    for area in areas:
        if area.type == 'INFO':
            area.tag_redraw()


# Inspired by: https://blog.michelanders.nl/2017/04/how-to-add-progress-indicator-to-the-info-header-in-blender.html
def register_custom_progress_bar() -> None:
    """Register the custom progress bar."""

    # Save the original draw method of Info header
    global info_header_draw
    info_header_draw = VIEW3D_HT_tool_header.draw

    # Create a new draw function
    def new_draw(self, context):
        global info_header_draw
        # First call to the original function
        info_header_draw(self, context)

        # Then add the prop that acts as a progress bar
        m_op_value = context.scene.tbb.m_op_value
        if m_op_value >= 0.0 and m_op_value <= 100.0:
            self.layout.separator()
            text = context.scene.tbb.m_op_label
            self.layout.prop(context.scene.tbb, "m_op_value", text=text, slider=True)

    # Replace the draw function by our new function
    # Blender crashes sometimes when using the progress bar in dev mode
    if not DEV_MODE:
        VIEW3D_HT_tool_header.draw = new_draw


# A variable where we can store the original draw function
def info_header_draw(s, c) -> None:  # noqa: D103
    return None
