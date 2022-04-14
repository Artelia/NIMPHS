# <pep8 compliant>
import bpy


def sequence_name_already_exist(user_sequence_name):
    for object in bpy.data.objects:
        if user_sequence_name + "_sequence" == object.name:
            return True

    return False
