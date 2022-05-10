# <pep8 compliant>
import bpy
from bpy.types import Context, Object

from src.properties.shared.module_scene_settings import TBB_ModuleSceneSettings


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


def lock_create_operator(settings: TBB_ModuleSceneSettings) -> tuple[bool, str]:
    """
    Check if we need to lock the 'create sequence' button.

    Args:
        settings (TBB_ModuleSceneSettings): scene settings

    Returns:
        tuple[bool, str]: ``True`` if it needs to be locked, error message if ``False``
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
    Return the selected object.

    Args:
        context (Context): context

    Returns:
        Object | None: selected object
    """

    obj = context.active_object
    # Even if no objects are selected, the last selected object remains in the active_objects variable
    if len(context.selected_objects) == 0:
        obj = None

    return obj
