# <pep8 compliant>
import bpy
from bpy.types import Context, Object, UILayout

from typing import Union

from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.properties.utils import VariablesInformation


def sequence_name_already_exist(name: str) -> bool:
    """
    Check if the given sequence name is already the name of an object. Will look for 'name' + '_sequence'.

    Args:
        name (str): possible name

    Returns:
        bool: ``True`` if the given name already exist
    """

    for object in bpy.data.objects:
        if name + "_sequence" == object.name:
            return True

    return False


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

        # Build info (value ranges)
        if values is not None:
            if point_data.remap_method == 'LOCAL':
                if values["local"]["min"] is not None and values["local"]["max"] is not None:
                    if type == 'SCALAR':
                        info = "[" + "{:.4f}".format(values["local"]["min"]) + " ; "
                        info += "{:.4f}".format(values["local"]["max"]) + "]"
                    if type == 'VECTOR':
                        info = ""
                        for i in range(dim):
                            info += "[" + "{:.4f}".format(values["local"]["min"][i]) + " ; "
                            info += "{:.4f}".format(values["local"]["max"][i]) + "]"
                else:
                    info = "None"
            elif point_data.remap_method == 'GLOBAL':
                if values["global"]["min"] is not None and values["global"]["max"] is not None:
                    if type == 'SCALAR':
                        info = "[" + "{:.4f}".format(values["global"]["min"]) + " ; "
                        info += "{:.4f}".format(values["global"]["max"]) + "]"
                    if type == 'VECTOR':
                        info = ""
                        for i in range(dim):
                            info += "[" + "{:.4f}".format(values["global"]["min"][i]) + " ; "
                            info += "{:.4f}".format(values["global"]["max"][i]) + "]"
                else:
                    info = "None"
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
