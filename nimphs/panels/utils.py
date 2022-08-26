# <pep8 compliant>
from bpy.types import Context, Object, UILayout

from typing import Union

from nimphs.properties.shared.point_data_settings import NIMPHS_PointDataSettings
from nimphs.properties.utils.point_data import PointDataInformation, PointDataManager


def get_selected_object(context: Context) -> Union[Object, None]:
    """
    Return the selected object.

    Args:
        context (Context): context

    Returns:
        Union[Object, None]: selected object
    """

    obj = context.active_object
    # Even if no objects are selected, the last selected object remains in the active_objects variable
    if len(context.selected_objects) == 0:
        return None

    if obj is None:
        return obj

    parent = obj.parent
    if parent is None:
        return obj

    if parent.type == 'EMPTY' and parent.nimphs.module in ['OpenFOAM', 'TELEMAC']:
        return parent

    return obj


def draw_point_data(layout: UILayout, point_data: NIMPHS_PointDataSettings, show_remap: bool = True,
                    show_range: bool = True, edit: bool = True, src: str = 'OBJECT') -> None:
    """
    Draw point data settings.

    Args:
        layout (UILayout): layout
        point_data (NIMPHS_PointDataSettings): point data settings
        src (str): which source is calling this function. Enum in ['OBJECT', 'OPERATOR'].
        show_remap (bool, optional): show remap method option. Defaults to True.
        show_range (bool, optional): show value ranges of selected point data. Defaults to True.
        edit (bool, optional): show edit buttons. Defaults to True.
    """

    if show_remap:
        row = layout.row()
        row.prop(point_data, "remap_method", text="Method")

    # Display selected point data
    data = PointDataManager(point_data.list)
    for name, unit, values in zip(data.names, data.units, data.ranges):

        if values is None:
            info = "None"

        else:
            value_range = values.get(point_data.remap_method)
            info = "[" + "{:.4f}".format(value_range[0]) + " ; "
            info += "{:.4f}".format(value_range[1]) + "]"

        subbox = layout.box()
        row = subbox.row()

        if edit:
            op = row.operator("nimphs.remove_point_data", text="", icon='REMOVE')
            op.var_name = name
            op.source = src

            if point_data.remap_method == 'CUSTOM':
                op = row.operator("nimphs.set_custom_value_range", text="", icon='GREASEPENCIL')
                op.chosen = PointDataInformation(name, unit, values).dumps()
                op.source = src
                # Force to show range
                show_range = True

        row.label(text=((name + ", (" + unit + ")") if unit != "" else name) + ((",  " + info) if show_range else ""))
