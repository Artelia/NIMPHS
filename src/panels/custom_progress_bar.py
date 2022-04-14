# <pep8 compliant>
from bpy.types import Scene, VIEW3D_HT_tool_header
from bpy.props import FloatProperty, StringProperty

DEV_MODE = True

# Inspired by: https://blog.michelanders.nl/2017/04/how-to-add-progress-indicator-to-the-info-header-in-blender.html

# Update function to tag all info areas for redraw


def update(self, context):
    areas = context.window.screen.areas
    for area in areas:
        if area.type == 'INFO':
            area.tag_redraw()


# A variable where we can store the original draw funtion
def info_header_draw(s, c): return None


def register_custom_progress_bar():
    # Use values between 0 and 100 to show the progress bar
    Scene.tbb_progress_value = FloatProperty(
        name="Progress value",
        default=-1.0,
        min=-1.0,
        soft_min=0.0,
        max=101.0,
        soft_max=100.0,
        precision=1,
        subtype="PERCENTAGE",
        update=update
    )

    # Label in front of the slider
    Scene.tbb_progress_label = StringProperty(
        name="Progress label",
        default="Progress",
        update=update
    )

    # Save the original draw method of Info header
    global info_header_draw
    info_header_draw = VIEW3D_HT_tool_header.draw

    # Create a new draw function
    def new_draw(self, context):
        global info_header_draw
        # First call to the original function
        info_header_draw(self, context)

        # Then add the prop that acts as a progress bar
        progress_value = context.scene.tbb_progress_value
        if progress_value >= 0.0 and progress_value <= 100.0:
            self.layout.separator()
            text = context.scene.tbb_progress_label
            self.layout.prop(context.scene, "tbb_progress_value", text=text, slider=True)

    # Replace the draw function by our new function
    # Blender crashes sometimes when using the progress bar in dev mode
    if not DEV_MODE:
        VIEW3D_HT_tool_header.draw = new_draw
