# <pep8 compliant>
from bpy.types import Context


def tbb_menus_draw(self, context: Context) -> None:  # noqa D417
    """
    Draw function for custom menus.

    Args:
        context (Context): context
    """

    if context.mode == 'OBJECT':
        self.layout.menu('TBB_MT_OpenfoamMainMenu')
        self.layout.menu('TBB_MT_TelemacMainMenu')
