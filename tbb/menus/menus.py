# <pep8 compliant>
from bpy.types import Context


def tbb_menus_draw(self, context: Context) -> None:
    if context.mode == 'OBJECT':
        self.layout.menu('TBB_MT_OpenfoamMainMenu')
