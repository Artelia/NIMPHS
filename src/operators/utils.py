# <pep8 compliant>
import bpy
from bpy.types import Collection, Object, Context, Mesh
from rna_prop_ui import rna_idprop_ui_create

import numpy as np
from typing import Any

from src.properties.shared.module_scene_settings import scene_settings_dynamic_props, TBB_ModuleSceneSettings
from src.properties.openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings
from src.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from src.properties.openfoam.Object.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty
from src.properties.telemac.Scene.telemac_settings import TBB_TelemacSettings


def generate_vertex_colors_groups(variables: list[dict]) -> list[dict]:
    """
    Generate optimized vertex colors groups.
    | Example: "FOND, VITESSE U, NONE" corresponds to: red channel = FOND, green channel = VITESS U, blue channel = NONE
    | Example: "k, p_rgh, alpha.water" corresponds to: red channel = k, green channel = p_rgh, blue channel = alpha.water

    :param variables: list of variables. Expected structure of each variable: {"name": str, "type": enum in ['VECTOR', 'SCALAR'], "id": Any}
    :type variables: list[dict]
    :raises AttributeError: if the given type of variable is undefined
    :return: vertex colors groups. Output structure of each group: {"name": str, "ids": [Any]}
    :rtype: list[dict]
    """

    group, groups, nb_vars_in_current_group = {"name": "", "ids": []}, [], 0

    # Util function to add a variable to the current group
    def add_var_to_group(name: str, id: Any) -> None:
        group["name"] += name + ", "
        group["ids"].append(id)

    # Util function to append a new group to the list of groups
    def append_group_to_groups() -> None:
        # Remove the comma at the end of the name
        group["name"] = group["name"][0:len(group["name"]) - 2]
        groups.append(group)

    for var in variables:
        if var["type"] == 'SCALAR':
            add_var_to_group(var["name"], var["id"])
            nb_vars_in_current_group += 1
        elif var["type"] == 'VECTOR':
            # If it is a vector value, add it as an entire group
            groups.append({"name": var["name"] + " (vector)", "ids": var["id"]})
        else:
            raise AttributeError("Variable type is undefined: '" + str(var["type"]) + "'")

        if nb_vars_in_current_group >= 3:
            append_group_to_groups()
            # Reset group data
            nb_vars_in_current_group = 0
            group["name"] = ""
            group["ids"].clear()

    # Add 'None' to the end of the last group if it is not full
    if nb_vars_in_current_group != 0 and nb_vars_in_current_group < 3:
        for i in range(3 - nb_vars_in_current_group):
            add_var_to_group("None", -1)

        append_group_to_groups()

    return groups


def generate_vertex_colors(blender_mesh: Mesh, groups: list[dict], data: np.ndarray, nb_vertex_ids: int) -> None:
    """
    Generate vertex colors for the given mesh.

    :param blender_mesh: mesh on which to add vertex colors.
    :type blender_mesh: Mesh
    :param groups: groups of vertex colors to create. Expected input for one group: {"name": str, ids: [Any]}.
    :type groups: list[dict]
    :param data: prepared data. Expected input: {id_var: np.ndarray, id_var: np.ndarray, ...}
    :type data: np.ndarray
    :param nb_vertex_ids: length of the list which contains all the vertex indices of all the triangles.
    :type nb_vertex_ids: int
    """

    # Data for alpha and empty channels
    ones = np.ones((nb_vertex_ids,))
    zeros = np.zeros((nb_vertex_ids,))

    for group in groups:
        vertex_colors = blender_mesh.vertex_colors.new(name=group["name"], do_init=True)

        colors = []
        for var_id in group["ids"]:
            if var_id != -1:
                colors.append(np.array(data[var_id]))
            else:
                colors.append(zeros)

        # Add ones for alpha channel
        colors.append(ones)

        # Reshape data
        colors = np.array(colors).T

        colors = colors.flatten()
        vertex_colors.data.foreach_set("color", colors)


def generate_object_from_data(vertices: np.ndarray, faces: np.ndarray, name: str) -> Object:
    """
    Generate an object and its mesh using the given vertices and faces.

    :param vertices: vertices, must have the following shape: (n, 3)
    :type vertices: np.ndarray
    :param faces: faces, must have the following shape: (n, 3)
    :type faces: np.ndarray
    :param name: name of the object
    :type name: str
    :return: generated object
    :rtype: Object
    """

    # Create the object (or write over it if it already exists)
    obj = bpy.data.objects.get(name)
    if obj is None:
        blender_mesh = bpy.data.meshes.get(name + "_mesh")
        if blender_mesh is None:
            blender_mesh = bpy.data.meshes.new(name + "_mesh")

        obj = bpy.data.objects.new(name, blender_mesh)
    else:
        blender_mesh = obj.data

    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return obj


def setup_streaming_sequence_object(obj: Object, seq_settings: TBB_OpenfoamStreamingSequenceProperty |
                                    TBB_TelemacStreamingSequenceProperty, time_points: int,
                                    settings: TBB_ModuleSceneSettings, module: str) -> None:

    # Setup common settings
    seq_settings.name = obj.name
    seq_settings.file_path = settings.file_path
    obj.tbb.is_streaming_sequence = True
    seq_settings.update = True
    obj.tbb.settings.module = module

    # Set the selected time frame
    seq_settings.frame_start = settings.frame_start     #
    seq_settings.max_length = time_points               # Order matters, check TBB_StreamingSequenceProperty class definition
    seq_settings.anim_length = settings["anim_length"]  #

    seq_settings.import_point_data = settings.import_point_data
    seq_settings.list_point_data = settings.list_point_data


def update_scene_settings_dynamic_props(settings: TBB_ModuleSceneSettings,
                                        tmp_data: TBB_OpenfoamSettings | TBB_TelemacSettings) -> None:
    """
    Update 'dynamic' settings of the main panel.
    It adapts the max values of properties in function of the imported file.

    :param settings: scene settings
    :type settings: TBB_SceneSettings
    :param tmp_data: temporary data
    :type tmp_data: TBB_OpenfoamSettings | TBB_TelemacSettings
    """

    # This works because TBB_TelemacTemporaryData and TBB_OpenfoamTemporaryData have the same nb_time_points attribute
    max_time_step = tmp_data.nb_time_points

    new_maxima = {
        "preview_time_point": max_time_step - 1,
        "start_time_point": max_time_step - 1,
        "end_time_point": max_time_step - 1,
        "anim_length": max_time_step,
    }
    update_dynamic_props(settings, new_maxima, scene_settings_dynamic_props)


def update_dynamic_props(settings: TBB_ModuleSceneSettings, new_maxima: dict, props: dict) -> None:
    """
    Set new max values to the given list of props.
    If a property does not exist, it creates it.

    :param settings: scene settings
    :type settings: TBB_SceneSettings
    :param new_maxima: dict of new maxima: {"prop_name": value, etc.}
    :type new_maxima: dict
    :param props: dict of properties: {"prop_name", "description", etc.}
    :type props: dict
    """

    for prop_id, prop_desc in props:
        if settings.get(prop_id) is None:
            rna_idprop_ui_create(
                settings,
                prop_id,
                default=0,
                min=0,
                soft_min=0,
                max=0,
                soft_max=0,
                description=prop_desc
            )

        prop = settings.id_properties_ui(prop_id)
        default = settings[prop_id]
        if new_maxima[prop_id] < default:
            default = 0
        prop.update(default=default, max=new_maxima[prop_id], soft_max=new_maxima[prop_id])


def get_collection(name: str, context: Context, link_to_scene: bool = True) -> Collection:
    """
    Get the collection called 'name'. If it does not exist, create it.

    :param name: name of the collection
    :type name: str
    :type context: Context
    :param link_to_scene: automatically link the collection to the list of scene collections, defaults to True
    :type link_to_scene: bool
    :return: the collection
    :rtype: Collection
    """

    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name=name)
        if link_to_scene:
            context.scene.collection.children.link(collection)

    return collection


def remap_array(input: np.ndarray, out_min: float = 0.0, out_max: float = 1.0,
                in_min: float = -np.inf, in_max: float = np.inf) -> np.ndarray:
    """
    Remap values of the given array.

    :param input: input array to remap
    :type input: np.ndarray
    :param out_min: minimum value to output, defaults to 0.0
    :type out_min: float, optional
    :param out_max: maximum value to output, defaults to 1.0
    :type out_max: float, optional
    :param in_min: minimum value of the input, defaults to -1.0
    :type in_min: float, optional
    :param in_max: maximum value of the input, defaults to 1.0
    :type in_max: float, optional
    :return: output array
    :rtype: np.ndarray
    """

    if in_min == -np.inf or in_max == np.inf:
        in_min = np.min(input)
        in_max = np.max(input)

    if out_min < np.finfo(np.float).eps and out_max < np.finfo(np.float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
