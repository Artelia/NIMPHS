# <pep8 compliant>
import bpy
from bpy.types import Collection, Object, Context, Mesh

import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Any

from tbb.operators.shared.create_streaming_sequence import TBB_CreateStreamingSequence


def generate_vertex_colors_groups(variables: list[dict]) -> list[dict]:
    """
    Generate optimized vertex colors groups.

    Some examples of outputs:

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


def generate_vertex_colors(bmesh: Mesh, groups: list[dict], data: np.ndarray, nb_vertex_ids: int) -> None:
    """
    Generate vertex colors for the given mesh.

    Args:
        bmesh (Mesh): mesh on which to add vertex colors
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
        vertex_colors = bmesh.vertex_colors.new(name=group["name"], do_init=True)

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


def generate_object_from_data(vertices: np.ndarray, faces: np.ndarray, name: str, new: bool = False) -> Object:
    """
    Generate an object and its mesh using the given vertices and faces.

    Args:
        vertices (np.ndarray): vertices, must have the following shape: (n, 3)
        faces (np.ndarray): faces, must have the following shape: (n, 3)
        name (str): name of the object
        new (bool): force to generate a new object

    Returns:
        Object: generated object
    """

    obj = bpy.data.objects.get(name) if not new else None
    if obj is None:
        blender_mesh = bpy.data.meshes.get(name + "_mesh") if not new else None
        if blender_mesh is None:
            blender_mesh = bpy.data.meshes.new(name + "_mesh")

        obj = bpy.data.objects.new(name, blender_mesh)
    else:
        blender_mesh = obj.data

    obj.shape_key_clear()
    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return obj


def setup_streaming_sequence_object(obj: Object, op: TBB_CreateStreamingSequence, file_path: str) -> None:
    """
    Generate streaming sequence settings for all modules.

    Args:
        obj (Object): sequence object
        op (TBB_CreateStreamingSequence): operator
        file_path (str): file path
    """

    # Get sequence settings
    if op.module == 'OpenFOAM':
        sequence = obj.tbb.settings.openfoam.s_sequence
    if op.module == 'TELEMAC':
        sequence = obj.tbb.settings.telemac.s_sequence

    # Setup common settings
    obj.tbb.settings.file_path = file_path
    obj.tbb.is_streaming_sequence = True
    obj.tbb.module = op.module

    # Setup sequence settings
    sequence.start = op.start                 # Order matters!
    sequence.max_length = op.max_length             # Check TBB_StreamingSequenceProperty class definition.
    sequence.length = op.length                #
    sequence.update = True


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

    if in_max - in_min > np.finfo(float).eps:
        return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
    else:
        return np.ones(shape=input.shape)
