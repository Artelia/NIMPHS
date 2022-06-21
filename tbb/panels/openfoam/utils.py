# <pep8 compliant>
from bpy.types import UILayout

from tbb.properties.utils import VariablesInformation
from tbb.properties.openfoam.openfoam_clip import TBB_OpenfoamClipProperty


def draw_clip_settings(layout: UILayout, clip: TBB_OpenfoamClipProperty, enable: bool = True) -> None:
    """
    Draw OpenFOAM clip settings.

    Args:
        layout (UILayout): layout
        clip (TBB_OpenfoamClipProperty): clip settings
        enable (bool): enable rows
    """

    box = layout.box()
    box.label(text="Clip")
    row = box.row()
    row.enabled = enable
    row.prop(clip, "type", text="Type")

    if clip.type == 'SCALAR':

        if clip.scalar.name != 'NONE':
            row = box.row()
            row.enabled = enable
            row.prop(clip.scalar, "name")

            row = box.row()
            row.enabled = enable

            var_type = VariablesInformation(clip.scalar.name).get(0, prop='TYPE')

            if var_type == 'VECTOR':
                row.prop(clip.scalar, "vector_value", text="Value")
            else:
                row.prop(clip.scalar, "value", text="Value")

            row = box.row()
            row.enabled = enable
            row.prop(clip.scalar, "invert")
        else:
            row = box.row()
            row.label(text="No data available.", icon='ERROR')
