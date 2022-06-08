# <pep8 compliant>
from bpy.types import Context, VIEW3D_HT_tool_header

DEV_MODE = True


def set_sequence_anim_length(self, value: int) -> None:
    """
    Function triggered when the user sets a new animation length. This let us to make sure the new value
    is not higher than the available time steps.

    Args:
        value (int): new value
    """

    if value > self.max_length:
        self["anim_length"] = self.max_length
    elif value < 0:
        self["anim_length"] = 0
    else:
        self["anim_length"] = value


def get_sequence_anim_length(self) -> int:
    """
    Return the animation length value.

    Returns:
        int: value
    """

    return self.get("anim_length", 0)


def update_progress_bar(_self, context: Context):
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
    """
    Register the custom progress bar.
    """

    # Save the original draw method of Info header
    global info_header_draw
    info_header_draw = VIEW3D_HT_tool_header.draw

    # Create a new draw function
    def new_draw(self, context):
        global info_header_draw
        # First call to the original function
        info_header_draw(self, context)

        # Then add the prop that acts as a progress bar
        progress_value = context.scene.tbb.progress_value
        if progress_value >= 0.0 and progress_value <= 100.0:
            self.layout.separator()
            text = context.scene.tbb.progress_label
            self.layout.prop(context.scene.tbb, "progress_value", text=text, slider=True)

    # Replace the draw function by our new function
    # Blender crashes sometimes when using the progress bar in dev mode
    if not DEV_MODE:
        VIEW3D_HT_tool_header.draw = new_draw


# A variable where we can store the original draw funtion
def info_header_draw(s, c):
    return None
