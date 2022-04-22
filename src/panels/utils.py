# <pep8 compliant>
import bpy


def sequence_name_already_exist(user_sequence_name: str) -> bool:
    """
    Tell if the given sequence name is already the name of an object.

    :param user_sequence_name: possible name
    :type user_sequence_name: str
    :rtype: bool
    """

    for object in bpy.data.objects:
        if user_sequence_name + "_sequence" == object.name:
            return True

    return False
