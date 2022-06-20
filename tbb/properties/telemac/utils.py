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
