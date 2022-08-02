# <pep8 compliant>
from bpy.types import Context, Object, UILayout

from typing import Union

from tbb.properties.utils.point_data import PointDataManager
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


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

    if parent.type == 'EMPTY' and parent.tbb.module in ['OpenFOAM', 'TELEMAC']:
        return parent

    return obj


def draw_point_data(layout: UILayout, point_data: TBB_PointDataSettings, show_remap: bool = True,
                    show_range: bool = True, edit: bool = True, src: str = 'OBJECT') -> None:
    """
    Draw point data settings.

    Args:
        layout (UILayout): layout
        point_data (TBB_PointDataSettings): point data settings
        src (str): which source is calling this function. Enum in ['OBJECT', 'OPERATOR'].
        show_remap (bool, optional): show remap method option. Defaults to True.
        show_range (bool, optional): show value ranges of selected point data. Defaults to True.
        edit (bool, optional): show edit buttons. Defaults to True.
    """

    if show_remap:
        row = layout.row()
        row.prop(point_data, "remap_method", text="Method")

        if point_data.remap_method == 'CUSTOM':
            row = layout.row()
            row.prop(point_data, "custom_remap_value", text="Value")

    # Display selected point data
    data = PointDataManager(point_data.list)
    for name, unit, values in zip(data.names, data.units, data.ranges):

        if values is None:
            info = "None"

        else:

            if point_data.remap_method == 'LOCAL':

                info = "[" + "{:.4f}".format(values.minL) + " ; "
                info += "{:.4f}".format(values.maxL) + "]"

            elif point_data.remap_method == 'GLOBAL':

                info = "[" + "{:.4f}".format(values.minG) + " ; "
                info += "{:.4f}".format(values.maxG) + "]"

            else:
                info = "None"

        subbox = layout.box()
        row = subbox.row()

        if edit:
            op = row.operator("tbb.remove_point_data", text="", icon='REMOVE')
            op.var_name = name
            op.source = src

        row.label(text=((name + ", (" + unit + ")") if unit != "" else name) + ((",  " + info) if show_range else ""))
