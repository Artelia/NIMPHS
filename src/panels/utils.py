# <pep8 compliant>
import bpy
from bpy.types import Context, Object

from ..properties.shared.scene_settings import TBB_SceneSettings


def sequence_name_already_exist(name: str) -> bool:
    """
    Return if the given sequence name is already the name of an object. Will look for 'name' + '_sequence'.

    :param user_sequence_name: possible name
    :type user_sequence_name: str
    :rtype: bool
    """

    for object in bpy.data.objects:
        if name + "_sequence" == object.name:
            return True

    return False


def lock_create_operator(settings: TBB_SceneSettings) -> tuple[bool, str]:
    """
    Return if we need to lock the 'create sequence' button.

    :param settings: scene settings
    :type settings: TBB_SceneSettings
    :return: state, error message if 'false'
    :rtype: tuple[bool, str]
    """

    snae = sequence_name_already_exist(settings.sequence_name)  # snae = sequence_name_already_exist
    snie = settings.sequence_name == "" or settings.sequence_name.isspace()  # snie = sequence name is empty
    if snae:
        message = "Name already taken"
    elif snie:
        message = "Name is empty"
    else:
        message = ""

    return snae or snie, message


def get_selected_object(context: Context) -> Object | None:
    """
    Return the selected object

    :type context: Context
    :rtype: Object | None
    """

    obj = context.active_object
    # Even if no objects are selected, the last selected object remains in the active_objects variable
    if len(context.selected_objects) == 0:
        obj = None

    return obj
