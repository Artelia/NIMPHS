# <pep8 compliant>
from bpy.types import Context, Object, UILayout

from typing import Union

from tbb.properties.utils import VariablesInformation
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
        obj = None

    return obj


def draw_point_data(layout: UILayout, point_data: TBB_PointDataSettings, show_range: bool = True,
                    edit: bool = True, src: str = 'OBJECT') -> None:
    """
    Draw point data settings.

    Args:
        layout (UILayout): layout
        point_data (TBB_PointDataSettings): point data settings
        src (str): which source is calling this function. Enum in ['OBJECT', 'OPERATOR/OpenFOAM', 'OPERATOR/TELEMAC'].
        show_range (bool, optional): show value ranges of selected point data. Defaults to True.
        edit (bool, optional): show edit buttons. Defaults to True.
    """

    row = layout.row()
    row.prop(point_data, "remap_method", text="Method")

    # Display selected point data
    data = VariablesInformation(point_data.list)
    for name, unit, values, type, dim in zip(data.names, data.units, data.ranges, data.types, data.dimensions):

        if values is None:
            info = "None"

        else:
            range_data = values[point_data.remap_method.lower()]

            if point_data.remap_method == 'LOCAL':

                if range_data["min"] is not None and range_data["max"] is not None:

                    if type == 'SCALAR':
                        info = "[" + "{:.4f}".format(range_data["min"]) + " ; "
                        info += "{:.4f}".format(range_data["max"]) + "]"

                    if type == 'VECTOR':
                        info = ""
                        for i in range(dim):
                            info += "[" + "{:.4f}".format(range_data["min"][i]) + " ; "
                            info += "{:.4f}".format(range_data["max"][i]) + "]"

                else:
                    info = "None"

            elif point_data.remap_method == 'GLOBAL':

                if range_data["min"] is not None and range_data["max"] is not None:

                    if type == 'SCALAR':
                        info = "[" + "{:.4f}".format(range_data["min"]) + " ; "
                        info += "{:.4f}".format(range_data["max"]) + "]"

                    if type == 'VECTOR':
                        info = ""
                        for i in range(dim):
                            info += "[" + "{:.4f}".format(range_data["min"][i]) + " ; "
                            info += "{:.4f}".format(range_data["max"][i]) + "]"

                else:
                    info = "None"
            else:
                info = "None"

        subbox = layout.box()
        row = subbox.row()

        if edit:
            op = row.operator("tbb.remove_point_data", text="", icon='REMOVE')
            op.var_name = name
            op.source = src

        row.label(text=(name + ", (" + unit + ")") if unit != "" else name + ((",  " + info) if show_range else ""))
