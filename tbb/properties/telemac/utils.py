# <pep8 compliant>
from bpy.types import Context


def remove_spaces_telemac_var_name(string: str) -> str:
    """
    Remove spaces at the end of the variable name (if the 16 characters are not used).

    Args:
        string (str): input string

    Returns:
        str: name
    """

    for i in range(len(string) - 1, -1, -1):
        if string[i] != " ":
            return string[:i + 1]

    return "NONE"


def update_var_names(self, context: Context) -> list:
    """
    Update the list of variable names for EnumProperties.

    Args:
        context (Context): context

    Returns:
        list: generated items
    """

    file_data = context.scene.tbb.settings.telemac.file_data
    names = file_data.vars["names"]
    units = file_data.vars["units"]

    items = []
    items.append(("-1", "None", "None"))
    for name, unit, id in zip(names, units, range(file_data.nb_vars)):
        items.append((str(id), name + ", (" + unit + ")", "Undocumented"))

    return items
