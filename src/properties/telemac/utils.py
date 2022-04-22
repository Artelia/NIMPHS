# <pep8 compliant>
from bpy.types import Context


def remove_spaces_telemac_var_name(string: str) -> str:
    for i in range(len(string) - 1, -1, -1):
        if string[i] != " ":
            return string[:i + 1]

    return "NONE"


def update_var_names(self, context: Context) -> list:
    tmp_data = context.scene.tbb_telemac_tmp_data
    names = tmp_data.variables_info["names"]
    units = tmp_data.variables_info["units"]

    items = []
    for name, unit, id in zip(names, units, range(tmp_data.nb_vars)):
        items.append((id, name + ", (" + unit + ")", "Undocumented"))

    return items
