# <pep8 compliant>
import bpy
from bpy.types import Collection, Mesh, Object, Context
from rna_prop_ui import rna_idprop_ui_create

from ..properties.scene_settings import scene_settings_dynamic_props

import numpy as np


def get_collection(name: str, context: Context, link_to_scene: bool = True) -> Collection:
    """
    Get the collection named 'name'. If it does not exist, create it.

    :param name: name of the collection
    :type name: str
    :type context: Context
    :param link_to_scene: automatically the collection to the list of scene collections, defaults to True
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


def generate_object_from_data(vertices: np.ndarray, faces: np.ndarray, name: str) -> tuple[Mesh, Object]:
    """
    Generate an object and its mesh using the given vertices and faces.

    :param vertices: vertices, must have the following shape: (n, 3)
    :type vertices: np.ndarray
    :param faces: faces, must have the following shape: (n, 3)
    :type faces: np.ndarray
    :param name: name of the preview object
    :type name: str
    :return: Blender mesh (of the generated object), generated object
    :rtype: tuple[Mesh, Object]
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

    return blender_mesh, obj


def update_scene_settings_dynamic_props(context: Context, type: str, settings, tmp_data) -> None:
    """
    Update 'dynamic' settings of the main panel. It adapts the max values of properties in function of the imported file.

    :type context: Context
    :param type: type of scene settings, enum in ['OpenFOAM', 'TELEMAC']
    :type type: str
    :param settings: scene settings
    :param tmp_data: temporary data
    """

    if type == 'OpenFOAM':
        max_time_step = tmp_data.file_reader.number_time_points
    else:
        max_time_step = tmp_data.nb_time_points

    new_maxima = {
        "preview_time_point": max_time_step - 1,
        "start_time_point": max_time_step - 1,
        "end_time_point": max_time_step - 1,
        "anim_length": max_time_step,
    }
    update_dynamic_props(settings, new_maxima, scene_settings_dynamic_props)


def update_dynamic_props(settings, new_maxima, props) -> None:
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


def poll_create_sequence(settings, context: Context) -> bool:
    """
    Common poll function for OpenFOAM and TELEMAC 'Create sequence' panels.

    :param settings: settings
    :type context: Context
    :rtype: bool
    """

    if settings.sequence_type == "mesh_sequence":
        return not context.scene.tbb_create_sequence_is_running and settings["start_time_point"] < settings["end_time_point"]
    elif settings.sequence_type == "streaming_sequence":
        return not context.scene.tbb_create_sequence_is_running
    else:  # Lock ui by default
        return False
