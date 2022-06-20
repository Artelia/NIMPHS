# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Mesh, Object, Context, Scene

import time
import json
import numpy as np
from typing import Union
from tbb.operators.telemac.Scene.telemac_create_mesh_sequence import TBB_OT_TelemacCreateMeshSequence
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.properties.utils import InterpInfoMeshSequence, InterpInfoStreamingSequence, InterpInfo
import logging

from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)

from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.properties.telemac.Object.telemac_mesh_sequence import TBB_TelemacMeshSequenceProperty
from tbb.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from tbb.operators.utils import (
    generate_object_from_data,
    remap_array,
    generate_vertex_colors_groups,
    generate_vertex_colors,)


def run_one_step_create_mesh_sequence_telemac(context: Context, op: TBB_OT_TelemacCreateMeshSequence) -> None:
    """
    Run one step of the 'create mesh sequence' for the TELEMAC module.

    Args:
        context (Context): context
        current_frame (int): current frame
        current_time_point (int): current time point
        start_time_point (int): start time point
        end_time_point (int): end time point
        user_sequence_name (str): user defined sequence name

    Raises:
        error: if something went wrong generating meshes
    """

    # First time point, create the sequence object
    if op.time_point == op.start:

        obj = generate_telemac_sequence_obj(context, op.obj, op.name, op.start, shape_keys=True)
        obj.tbb.module = 'TELEMAC'
        obj.tbb.is_mesh_sequence = True
        obj.tbb.settings.file_path = op.obj.tbb.settings.file_path
        # Copy point data settings
        obj.tbb.settings.point_data.import_data = op.point_data.import_data
        obj.tbb.settings.point_data.list = op.point_data.list
        obj.tbb.settings.point_data.remap_method = op.point_data.remap_method
        context.scene.collection.objects.link(obj)

    # Other time points, update vertices
    else:
        obj = bpy.data.objects[op.name + "_sequence"]
        tmp_data = context.scene.tbb.tmp_data.get(obj.tbb.uid, None)

        for child, id in zip(obj.children, range(len(obj.children))):
            if not tmp_data.is_3d:
                type = child.tbb.settings.telemac.z_name
                vertices = generate_mesh_data(tmp_data, op.time_point, type=type)
            else:
                vertices = generate_mesh_data(tmp_data, op.time_point, offset=id)

            set_new_shape_key(child, vertices.flatten(), str(op.time_point), op.frame, op.time_point == op.end)


def generate_mesh_data(tmp_data: TBB_TelemacTemporaryData, time_point: int, offset: int = 0,
                       type: str = 'BOTTOM') -> np.ndarray:
    """
    Generate the mesh of the selected file. If the selected file is a 2D simulation, you can precise\
    which part of the mesh you want ('BOTTOM' or 'WATER_DEPTH'). If the file is a 3D simulation, you can\
    precise an offset for data reading (this offsets is somehow the id of the plane to generate).

    Args:
        tmp_data (TBB_TelemacTemporaryData): temporary data
        mesh_is_3d (bool): if the mesh is from a 3D simulation
        offset (int, optional): if the mesh is from a 3D simulation, precise the offset in the data to read.\
            Defaults to 0.
        time_point (int, optional): time point from which to read data. Defaults to 0.
        type (str, optional): type of the object, enum in ['BOTTOM', 'WATER_DEPTH']. Defaults to 'BOTTOM'.

    Returns:
        np.ndarray: vertices of the mesh, shape is (number_of_vertices, 3)
    """

    if not tmp_data.is_3d and type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    # If file from a 3D simulation
    if tmp_data.is_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
        except Exception:
            z_values = np.zeros((tmp_data.nb_vertices, 1))
            log.error(f"No data available from var names {possible_var_names}", exc_info=1)

        # Ids from where to read data in the z_values array
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        vertices = np.hstack((tmp_data.vertices, z_values[start_id:end_id]))

    # If file from a 2D simulation
    else:
        if type == 'BOTTOM':
            possible_var_names = ["BOTTOM", "FOND"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
            except Exception:
                z_values = np.zeros((tmp_data.nb_vertices, 1))
                log.error(f"No data available from var names {possible_var_names}", exc_info=1)

            vertices = np.hstack((tmp_data.vertices, z_values))

        if type == 'WATER_DEPTH':
            possible_var_names = ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)

                # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                if var_name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                    bottom, var_name = tmp_data.get_data_from_possible_var_names(["BOTTOM", "FOND"], time_point)
                    z_values += bottom

            except Exception:
                z_values = np.zeros((tmp_data.nb_vertices, 1))
                log.error(f"No data available from var names {possible_var_names}", exc_info=1)

            vertices = np.hstack((tmp_data.vertices, z_values))

    return vertices


def generate_mesh_data_linear_interp(obj: Object, tmp_data: TBB_TelemacTemporaryData, time_info: InterpInfo,
                                     offset: int = 0) -> np.ndarray:
    """
    Linearly interpolates the mesh of the given TELEMAC object.

    Args:
        obj (Object): object to interpolate
        tmp_data (TBB_TelemacTemporaryData): temporary data

        offset (int): corresponds to 'plane id' for meshes from 3D simulations. Defaults to 0.

    Raises:
        vertices_error: if something went wrong generating mesh data

    Returns:
        np.ndarray: vertices
    """

    # Get data from left time point
    left = generate_mesh_data(tmp_data, time_info.left, offset=offset, type=obj.tbb.settings.telemac.z_name)

    if not time_info.exists:
        # Get data from right time point
        right = generate_mesh_data(tmp_data, time_info.right, offset=offset, type=obj.tbb.settings.telemac.z_name)

        percentage = np.abs(time_info.frame - time_info.left) / (time_info.time_steps + 1)

        return (left.T + (right.T - left.T) * percentage).T

    else:
        # If it is an existing time point, no need to interpolate
        return left


def generate_base_objects(tmp_data: TBB_TelemacTemporaryData, time_point: int, name: str,
                          point_data: Union[TBB_PointDataSettings, str] = "") -> list[Object]:
    """
    Generate objects using settings defined by the user. This function generates objects and vertex colors.

    If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth"). If the file
    is a 3D simulation, this will generate one object per plane.

    Args:
        time_point (int): time point from which to read data
        name (str): name of the objects
        import_point_data (bool, optional): import point data as vertex colors. Defaults to False.
        point_data (str, optional): JSON stringified deict of point data to import as vertex colors groups.\
                                    Defaults to "".

    Returns:
        list[Object]: generated object
    """

    # Check if we need to import point data
    if isinstance(point_data, str):
        import_point_data = point_data != ""
    else:
        import_point_data = point_data.import_data

    objects = []
    if not tmp_data.is_3d:
        for type in ['BOTTOM', 'WATER_DEPTH']:
            vertices = generate_mesh_data(tmp_data, time_point, type=type)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_" + type.lower())
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = type

            if import_point_data:
                res = prepare_telemac_point_data(obj.data, point_data, tmp_data, time_point)
                generate_vertex_colors(obj.data, *res)

            objects.append(obj)
    else:
        for plane_id in range(tmp_data.nb_planes - 1, -1, -1):
            vertices = generate_mesh_data(tmp_data, time_point, offset=plane_id)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_plane_" + str(plane_id))
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = str(plane_id)

            if import_point_data:
                res = prepare_telemac_point_data(obj.data, point_data, tmp_data, time_point, offset=plane_id)
                generate_vertex_colors(obj.data, *res)

            objects.append(obj)

    return objects


def generate_preview_material(obj: Object, var_name: str, name: str = "TBB_TELEMAC_preview_material") -> None:
    """
    Generate the preview material (if not generated yet). Update it otherwise (with the new variable).

    This generates the following node tree:

    .. code-block:: text

        {Vertex color}[color] >>> [image]{Separate RBG}[R, G, B] >>> [color]{Principled BSDF}

    Args:
        obj (Object): object on which to apply the material
        var_name (str): name of the variable to preview
        name (str, optional): name of the material. Defaults to "TBB_TELEMAC_preview_material".

    Raises:
        NameError: if the variable is not found in the vertex colors groups
    """

    # Get the preview material
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True

    # Get channel and vertex colors group for the given variable name
    channel_id, group_name = np.inf, np.inf
    for group in obj.data.vertex_colors:
        names = group.name.split(", ")
        for name, chan_id in zip(names, range(len(names))):
            if name == var_name:
                channel_id, group_name = chan_id, group.name

    if channel_id == np.inf:
        raise NameError("Variable " + str(var_name) + " not found in vertex colors data")

    # Get node tree
    mat_node_tree = material.node_tree

    vertex_color_node = mat_node_tree.nodes.get(name + "_vertex_color")
    if vertex_color_node is None:
        vertex_color_node = mat_node_tree.nodes.new(type="ShaderNodeVertexColor")
        vertex_color_node.name = name + "_vertex_color"
        vertex_color_node.location = (-500, 250)

    separate_rgb_node = mat_node_tree.nodes.get(name + "_separate_rgb")
    if separate_rgb_node is None:
        separate_rgb_node = mat_node_tree.nodes.new(type="ShaderNodeSeparateRGB")
        separate_rgb_node.name = name + "_separate_rgb"
        separate_rgb_node.location = (-250, 250)
        mat_node_tree.links.new(vertex_color_node.outputs[0], separate_rgb_node.inputs[0])

    principled_bsdf_node = mat_node_tree.nodes.get("Principled BSDF")
    # No need to remove old links thanks to the 'verify limits' argument
    mat_node_tree.links.new(separate_rgb_node.outputs[channel_id], principled_bsdf_node.inputs[0])

    # Update vertex colors group to preview
    vertex_color_node.layer_name = group_name
    # Make sure it is the active material
    obj.active_material = material


def generate_telemac_sequence_obj(context: Context, obj: Object, name: str, time_point: int,
                                  shape_keys: bool = False) -> Object:
    """
    Generate base object for a TELEMAC sequence.

    Args:
        context (Context): context
        name (str): name of the sequence

    Returns:
        Object: generate object
    """

    # Create sequence object
    sequence = bpy.data.objects.new(name=name + "_sequence", object_data=None)

    # Load temporary data
    sequence.tbb.uid = str(time.time())
    context.scene.tbb.tmp_data[sequence.tbb.uid] = TBB_TelemacTemporaryData(obj.tbb.settings.file_path, False)
    sequence.tbb.settings.telemac.is_3d_simulation = obj.tbb.settings.telemac.is_3d_simulation

    try:
        children = generate_base_objects(context.scene.tbb.tmp_data[sequence.tbb.uid], time_point, name + "_sequence")
    except Exception as error:
        raise error

    for child in children:
        if shape_keys:
            # Add 'Basis' shape key
            child.shape_key_add(name="Basis", from_mix=False)
        # Add the object to the collection
        context.scene.collection.objects.link(child)
        # Parent object
        child.parent = sequence

    return sequence


def prepare_telemac_point_data(bmesh: Mesh, point_data: Union[TBB_PointDataSettings, str],
                               tmp_data: TBB_TelemacTemporaryData, time_point: int,
                               offset: int = 0) -> tuple[list[dict], dict, int]:
    """
    Prepare point data for the 'generate_vertex_colors' function.

    Args:
        obj (Object): object
        settings (TBB_ObjectSettings): sequence object settings
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_point (int): time point from which to read data
        offset (int, optional): if the mesh is from a 3D simulation, precise the offset in the data to read.\
            Defaults to 0.

    Returns:
        tuple[list[dict], dict, int]: vertex colors groups, data, nb_vertex_ids
    """

    # Prepare the mesh to loop over all its triangles
    if len(bmesh.loop_triangles) == 0:
        bmesh.calc_loop_triangles()

    vertex_ids = np.array([triangle.vertices for triangle in bmesh.loop_triangles]).flatten()

    # Format variables array
    variables, dimensions = [], []
    info = VariablesInformation(point_data if isinstance(point_data, str) else point_data.list)
    for var, type, dim in zip(info.names, info.types, info.dimensions):
        if var != "None":
            variables.append({"name": var, "type": type, "id": var})
            dimensions.append(dim)

    # Prepare data
    prepared_data = dict()
    method = 'LOCAL' if isinstance(point_data, str) else point_data.remap_method

    # Note: dim is always 1 (scalars)
    for var, id in zip(variables, range(len(variables))):
        # Read data
        data = tmp_data.get_data_from_var_name(var["id"], time_point, output_shape='ROW')
        var_ranges = info.get(id, prop='RANGE')

        # Get right range of data in case of 3D simulation
        if tmp_data.is_3d:
            start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
            data = data[start_id:end_id]

        # Remap data
        if method == 'LOCAL':
            min, max = var_ranges["local"]["min"], var_ranges["local"]["max"]
            prepared_data[var["id"]] = remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max)
        elif method == 'GLOBAL':
            min, max = var_ranges["global"]["min"], var_ranges["global"]["max"]
            prepared_data[var["id"]] = remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max)
        else:
            prepared_data[var["id"]] = np.array(data)[vertex_ids]

    return generate_vertex_colors_groups(variables), prepared_data, len(vertex_ids)


def prepare_telemac_point_data_linear_interp(bmesh: Mesh, point_data: TBB_PointDataSettings,
                                             tmp_data: TBB_TelemacTemporaryData, time_info: InterpInfo,
                                             offset: int = 0) -> tuple[list[dict], dict, int]:
    """
    Prepare point data for linear interpolation of TELEMAC sequences.

    Args:
        obj (Object): object to interpolate
        settings (TBB_ObjectSettings): sequence object settings
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_info (InterpInfo): interpolation information
        offset (int): corresponds to 'plane id' for meshes from 3D simulations. Defaults to 0.

    Returns:
        tuple[list[dict], dict, int]: vertex colors groups, data, nb_vertex_ids
    """

    # Get data from left time point
    left = prepare_telemac_point_data(bmesh, point_data, tmp_data, time_info.left, offset=offset)

    if not time_info.exists:
        # Get data from right time point
        right = prepare_telemac_point_data(bmesh, point_data, tmp_data, time_info.right, offset=offset)

        percentage = np.abs(time_info.frame - time_info.left_frame) / (time_info.time_steps + 1)

        # Linearly interpolate
        data = left
        for id in data[1].keys():
            data[1][id] = left[1][id] + (right[1][id] - left[1][id]) * percentage

        return data

    else:
        # If it is an existing time point, no need to interpolate
        return left


def set_new_shape_key(obj: Object, vertices: np.ndarray, name: str, frame: int, end: bool) -> None:
    """
    Add a shape key to the object using the given vertices. It also set a keyframe with value = 1.0 at the given frame\
    and add keyframes at value = 0.0 around the frame (-1 and +1).

    Args:
        obj (Object): object to receive the new shape key
        vertices (np.ndarray): new vertices values
        name (str): name of the shape key
        frame (int): the frame on which the keyframe is inserted
        end (bool): indicate if this the shape key to add is the last one. Defaults to False.
    """

    obj.data.vertices.foreach_set("co", vertices.flatten())

    # Add a shape key
    block = obj.shape_key_add(name=name, from_mix=False)
    block.value = 1.0
    # Keyframe the new shape key
    block.keyframe_insert("value", frame=frame, index=-1)
    block.value = 0.0
    block.keyframe_insert("value", frame=frame - 1, index=-1)
    if not end:
        block.keyframe_insert("value", frame=frame + 1, index=-1)


@persistent
def update_telemac_streaming_sequences(scene: Scene) -> None:
    """
    App handler appended to the frame_change_pre handlers.

    Updates all the TELEMAC 'streaming sequences' of the scene.

    Args:
        scene (Scene): scene
    """

    frame = scene.frame_current

    if not scene.tbb.create_sequence_is_running:
        for obj in scene.objects:
            sequence = obj.tbb.settings.telemac.s_sequence
            interpolate = obj.tbb.settings.telemac.interpolate

            if obj.tbb.is_streaming_sequence and sequence.update:
                # Get temporary data
                try:
                    tmp_data = scene.tbb.tmp_data[obj.tbb.uid]
                except KeyError:
                    # Disable update
                    sequence.update = False
                    log.error(f"No file data available for {obj.name}. Disabling update.")
                    return

                # Compute limit (takes interpolation into account)
                limit = sequence.start + sequence.length
                if interpolate.type != 'NONE':
                    limit += (sequence.length - 1) * interpolate.time_steps

                if frame >= sequence.start and frame < limit:
                    start = time.time()

                    for child, id in zip(obj.children, range(len(obj.children))):
                        offset = id if tmp_data.is_3d else 0
                        update_telemac_streaming_sequence_mesh(obj, child, tmp_data, frame, offset)

                    log.info(obj.name + ", " + "{:.4f}".format(time.time() - start) + "s")


def update_telemac_streaming_sequence_mesh(obj: Object, child: Object, tmp_data: TBB_TelemacTemporaryData,
                                           frame: int, offset: int) -> None:
    """
    Update the mesh of the given object from a TELEMAC 'streaming sequence' object.

    It also manages interpolation.

    Args:
        obj (Object): object from a TELEMAC sequence object
        settings (TBB_ObjectSettings): 'streaming sequence' settings
        frame (int): current frame
        offset (int): id of the current object (used for meshes from 3D simulations, corresponds to the 'plane id')
        tmp_data (TBB_TelemacTemporaryData): temporary data

    Raises:
        tmp_data_error: if something went wrong loading the file
        mesh_error: if something went wrong generating mesh data
        point_data_error: if something went wrong generating vertex colors data
        ValueError: if the given time point does not exist
    """

    # Get settings
    interpolate = obj.tbb.settings.telemac.interpolate
    sequence = obj.tbb.settings.telemac.s_sequence
    point_data = obj.tbb.settings.point_data

    # Get time information
    if interpolate.type == 'LINEAR':
        time_info = InterpInfoStreamingSequence(frame, sequence.start, interpolate.time_steps)
    else:
        time_point = frame - sequence.start

    # Update mesh
    if interpolate.type == 'LINEAR':
        vertices = generate_mesh_data_linear_interp(child, tmp_data, time_info, offset)
    elif interpolate.type == 'NONE':
        vertices = generate_mesh_data(tmp_data, time_point, offset=offset, type=child.tbb.settings.telemac.z_name)

    # Generate object
    child = generate_object_from_data(vertices, tmp_data.faces, child.name)

    # Update point data
    if point_data.import_data:
        # Remove old vertex colors
        while child.data.vertex_colors:
            child.data.vertex_colors.remove(child.data.vertex_colors[0])

        # Update vertex colors data
        if interpolate.type == 'LINEAR':
            res = prepare_telemac_point_data_linear_interp(child.data, point_data, tmp_data, time_info, offset=offset)
        elif interpolate.type == 'NONE':
            res = prepare_telemac_point_data(child.data, point_data, tmp_data, time_point, offset=offset)

        generate_vertex_colors(child.data, *res)


@persistent
def update_telemac_mesh_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'mesh sequence' objects.

    Args:
        scene (Scene): scene
    """

    if not scene.tbb.create_sequence_is_running:
        for obj in scene.objects:
            point_data = obj.tbb.settings.point_data

            if obj.tbb.is_mesh_sequence and point_data.import_data:
                sequence = obj.tbb.settings.telemac.m_sequence

                # Get temporary data
                try:
                    tmp_data = scene.tbb.tmp_data[obj.tbb.uid]
                except KeyError:
                    # Disable update
                    sequence.update = False
                    log.error(f"No file data available for {obj.name}. Disabling update.")
                    return

                # Update children of the sequence object
                cumulated_time = 0.0

                for child, id in zip(obj.children, range(len(obj.children))):
                    start = time.time()

                    # Get interpolation time information
                    time_info = InterpInfoMeshSequence(child, scene.frame_current)
                    if time_info.has_data:
                        offset = id if tmp_data.is_3d else 0
                        update_telemac_mesh_sequence(child.data, tmp_data, offset, point_data, time_info)

                    cumulated_time += time.time() - start

                if cumulated_time > 0.0:
                    log.info(obj.name + ", " + "{:.4f}".format(cumulated_time) + "s")


def update_telemac_mesh_sequence(bmesh: Mesh, tmp_data: TBB_TelemacTemporaryData, offset: int,
                                 point_data: TBB_PointDataSettings, time_info: InterpInfo) -> None:
    """
    Update vertex colors of the given TELEMAC 'Mesh Sequence' child object.

    Args:
        bmesh (Mesh): blender mesh
        tmp_data (TBB_TelemacTemporaryData): temporary data
        offset (int): _description_
        point_data (TBB_PointDataSettings): point data
        time_info (InterpInfo): interpolation time information
    """

    # Remove existing vertex colors
    while bmesh.vertex_colors:
        bmesh.vertex_colors.remove(bmesh.vertex_colors[0])

    # Update point data
    res = prepare_telemac_point_data_linear_interp(bmesh, point_data, tmp_data, time_info, offset=offset)
    generate_vertex_colors(bmesh, *res)
