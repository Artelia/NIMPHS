# <pep8 compliant>
import bpy
from rna_prop_ui import rna_idprop_ui_create
from bpy.types import Collection, Object, Context, Mesh

import numpy as np
from typing import Any, Union

from tbb.properties.telemac.Scene.telemac_settings import TBB_TelemacSettings
from tbb.properties.openfoam.Scene.openfoam_settings import TBB_OpenfoamSettings
from tbb.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from tbb.properties.openfoam.Object.openfoam_streaming_sequence import TBB_OpenfoamStreamingSequenceProperty
from tbb.properties.shared.module_scene_settings import scene_settings_dynamic_props, TBB_ModuleSceneSettings


def generate_vertex_colors_groups(variables: list[dict]) -> list[dict]:
    """
    Generate optimized vertex colors groups. Some examples of outputs:

    .. code-block:: text

        Example: "k, p_rgh, alpha.water" means: (R = k, G = p_rgh, B = alpha.water)
        Example: "U.x, U.y, U.z" means: (R = U.x, G = U.y, B = U.z)
        Example: "FOND, VITESSE U, NONE" means: (R = FOND, G = VITESSE U, B = NONE)

    Args:
        variables (list[dict]): list of variables.\
            Expected structure of each variable: ``{"name": str, "type": enum in ['VECTOR', 'SCALAR'], "id": Any}``

    Raises:
        AttributeError: if the given type of variable is undefined

    Returns:
        list[dict]: vertex colors groups.\
        Output structure of each group: ``{"name": str, "ids": [Any]}``
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
        groups.append({"name": group["name"], "ids": group["ids"]})

    for var in variables:
        if var["type"] == 'SCALAR':
            add_var_to_group(var["name"], var["id"])
            nb_vars_in_current_group += 1
        elif var["type"] == 'VECTOR':
            # If it is a vector value, add it as an entire group
            name = var["name"] + ".x, " + var["name"] + ".y, " + var["name"] + ".z"
            groups.append({"name": name, "ids": [var["id"]]})
        else:
            raise AttributeError("Variable type is undefined: '" + str(var["type"]) + "'")

        if nb_vars_in_current_group >= 3:
            append_group_to_groups()
            # Reset group data
            nb_vars_in_current_group = 0
            group["name"] = ""
            group["ids"] = []

    # Add 'None' to the end of the last group if it is not full
    if nb_vars_in_current_group != 0 and nb_vars_in_current_group < 3:
        for i in range(3 - nb_vars_in_current_group):
            add_var_to_group("None", -1)

        append_group_to_groups()

    return groups


def generate_vertex_colors(blender_mesh: Mesh, groups: list[dict], data: np.ndarray, nb_vertex_ids: int) -> None:
    """
    Generate vertex colors for the given mesh.

    Args:
        blender_mesh (Mesh): mesh on which to add vertex colors
        groups (list[dict]): groups of vertex colors to create.\
            Expected input for one group: ``{"name": str, ids: [Any]}``.
        data (np.ndarray):  prepared data.\
            Expected input: ``{id_var: np.ndarray, id_var: np.ndarray, ...}``
        nb_vertex_ids (int): length of the list which contains all the vertex indices of all the triangles.
    """

    # Data for alpha and empty channels
    ones = np.ones((nb_vertex_ids,))
    zeros = np.zeros((nb_vertex_ids,))

    for group in groups:
        vertex_colors = blender_mesh.vertex_colors.new(name=group["name"], do_init=True)

        colors = []
        # Scalar value
        if len(group["ids"]) > 1:
            for var_id in group["ids"]:
                if var_id != -1:
                    colors.append(np.array(data[var_id]))
                else:
                    colors.append(zeros)
        # Vector value
        else:
            colors = data[group["ids"][0]]

        # Add ones for alpha channel
        colors.append(ones)

        # Reshape data
        colors = np.array(colors).T

        colors = colors.flatten()
        vertex_colors.data.foreach_set("color", colors)


def generate_object_from_data(vertices: np.ndarray, faces: np.ndarray, name: str) -> Object:
    """
    Generate an object and its mesh using the given vertices and faces.

    Args:
        vertices (np.ndarray): vertices, must have the following shape: (n, 3)
        faces (np.ndarray): faces, must have the following shape: (n, 3)
        name (str): name of the object

    Returns:
        Object: generated object
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

    obj.shape_key_clear()
    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return obj


def setup_streaming_sequence_object(obj: Object, seq_settings: Union[TBB_OpenfoamStreamingSequenceProperty,
                                    TBB_TelemacStreamingSequenceProperty], time_points: int,
                                    settings: TBB_ModuleSceneSettings, module: str) -> None:
    """
    Setup streaming sequence settings for both OpenFOAM and TELEMAC modules.

    Args:
        obj (Object): sequence object
        seq_settings Union[TBB_OpenfoamStreamingSequenceProperty, TBB_TelemacStreamingSequenceProperty]: settings
        time_points (int): number of available time points
        settings (TBB_ModuleSceneSettings): scene settings
        module (str): name of the module, enum in ['OpenFOAM', 'TELEMAC']
    """

    # Setup common settings
    seq_settings.name = obj.name
    seq_settings.file_path = settings.file_path
    obj.tbb.is_streaming_sequence = True
    seq_settings.update = True
    obj.tbb.settings.module = module

    # Set the selected time frame
    seq_settings.frame_start = settings.frame_start     # Order matters!
    seq_settings.max_length = time_points               # Check TBB_StreamingSequenceProperty class definition.
    seq_settings.anim_length = settings["anim_length"]  #

    seq_settings.import_point_data = settings.import_point_data
    seq_settings.list_point_data = settings.list_point_data


def update_scene_settings_dynamic_props(settings: TBB_ModuleSceneSettings,
                                        tmp_data: Union[TBB_OpenfoamSettings, TBB_TelemacSettings]) -> None:
    """
    Update 'dynamic' settings of the main panel.
    It adapts the max values of properties in function of the imported file.

    Args:
        settings (TBB_ModuleSceneSettings): scene settings
        tmp_data Union[TBB_OpenfoamSettings, TBB_TelemacSettings]: temporary data
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
    Set new max values to the given list of props. If a property does not exist, create it.

    Args:
        settings (TBB_ModuleSceneSettings): scene settings
        new_maxima (dict): dict of new maxima: ``{"prop_name": value, ...}``
        props (dict): dict of properties: ``[(prop_name, description), ...]``
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

    Args:
        name (str): name of the collection
        context (Context): context
        link_to_scene (bool, optional): automatically link the collection to the list of scene collections.\
            Defaults to True.

    Returns:
        Collection: collection
    """

    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name=name)
        if link_to_scene:
            context.scene.collection.children.link(collection)

    return collection


def get_object_dimensions_from_mesh(obj: Object) -> list[float]:
    """
    Compute the dimensions of the object from its mesh.

    Args:
        obj (Object): object

    Returns:
        list[float]: ``(x, y, z)`` dimensions
    """

    dimensions = []
    vertices = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
    obj.data.vertices.foreach_get("co", vertices)
    vertices = vertices.reshape((int(len(vertices) / 3)), 3)
    dimensions.append(np.max(vertices[:, 0]) - np.min(vertices[:, 0]))
    dimensions.append(np.max(vertices[:, 1]) - np.min(vertices[:, 1]))
    dimensions.append(np.max(vertices[:, 2]) - np.min(vertices[:, 2]))
    return dimensions


def normalize_objects(objects: list[Object], dimensions: list[float]) -> None:
    """
    Rescale the given list of objects so coordinates of all the meshes are now in the range [-1;1].

    Args:
        objects (list[Object]): objects to normalize
        dimensions (list[float]): original dimensions
    """

    factor = 1.0 / np.max(dimensions)
    rescale_objects(objects, [factor, factor, factor])


def rescale_objects(objects: list[Object], dimensions: list[float], apply: bool = False) -> None:
    """
    Resize a collection using the given dimensions.

    Args:
        objects (list[Object]): objects to normalize
        dimensions (list[float]): target dimensions
        apply (bool, optional): apply the rescale for each object in the given list. Defaults to False.
    """

    if apply:
        # Deselect everything so we make sure the transform_apply will only be applied to our meshes
        bpy.ops.object.select_all(action='DESELECT')

    for obj in objects:
        if apply:
            obj.select_set(True)
        obj.scale = dimensions

    if apply:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        for obj in objects:
            obj.select_set(False)


def remap_array(input: np.ndarray, out_min: float = 0.0, out_max: float = 1.0,
                in_min: float = -np.inf, in_max: float = np.inf) -> np.ndarray:
    """
    Remap values of the given array.

    Args:
        input (np.ndarray): input array to remap
        out_min (float, optional): minimum value to output. Defaults to 0.0.
        out_max (float, optional): maximum value to output. Defaults to 1.0.
        in_min (float, optional): minimum value of the input. Defaults to -np.inf.
        in_max (float, optional): maximum value of the input. Defaults to np.inf.

    Returns:
        np.ndarray: output array
    """

    if in_min == -np.inf or in_max == np.inf:
        in_min = np.min(input)
        in_max = np.max(input)

    if out_min < np.finfo(float).eps and out_max < np.finfo(float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
