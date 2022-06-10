# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Mesh, Object, Context, Scene

import time
import json
import numpy as np
from typing import Union

from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.properties.telemac.telemac_interpolate import TBB_TelemacInterpolateProperty
from tbb.properties.telemac.Object.telemac_mesh_sequence import TBB_TelemacMeshSequenceProperty
from tbb.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from tbb.operators.utils import (
    generate_object_from_data,
    remap_array,
    get_collection,
    generate_vertex_colors_groups,
    generate_vertex_colors,
    get_object_dimensions_from_mesh,
    normalize_objects)


def run_one_step_create_mesh_sequence_telemac(context: Context, current_frame: int, current_time_point: int,
                                              start_time_point: int, end_time_point: int, user_sequence_name: str):
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

    settings = context.scene.tbb.settings.telemac
    tmp_data = settings.tmp_data
    seq_obj_name = user_sequence_name + "_sequence"

    # First time point, create the sequence object
    if current_time_point == start_time_point:

        collection = get_collection("TBB_TELEMAC", context)

        try:
            objects = generate_base_objects(context, start_time_point, name=seq_obj_name)

            for obj in objects:
                # Add 'Basis' shape key
                obj.shape_key_add(name="Basis", from_mix=False)
                # Add the object to the collection
                collection.objects.link(obj)

            # Normalize if needed (option set by the user)
            if settings.normalize_sequence_obj:
                normalize_objects(objects, get_object_dimensions_from_mesh(objects[0]))

        except Exception as error:
            raise error

        # Create the sequence object
        seq_obj = bpy.data.objects.new(name=seq_obj_name, object_data=None)
        seq_obj.tbb.is_mesh_sequence = True
        seq_obj.tbb.import_point_data = settings.import_point_data
        seq_obj.tbb.settings.telemac.m_sequence.point_data = settings.point_data
        seq_obj.tbb.settings.telemac.m_sequence.is_3d_simulation = tmp_data.is_3d
        seq_obj.tbb.settings.telemac.m_sequence.file_path = settings.file_path

        # Add temporary data to the dictionary of tmp_data in TBB_Object
        # WARNING: temporary data dictionary is also temporary (class attribute, not saved in the .blend file)
        seq_obj.tbb.uid = str(time.time())
        seq_obj.tbb.tmp_data[seq_obj.tbb.uid] = TBB_TelemacTemporaryData()
        seq_obj.tbb.tmp_data[seq_obj.tbb.uid].update(settings.file_path)

        # Parent objects
        for child in objects:
            child.parent = seq_obj

        collection.objects.link(seq_obj)

    # Other time points, update vertices
    else:
        seq_obj = bpy.data.objects[seq_obj_name]
        time_point = current_time_point

        for obj, id in zip(seq_obj.children, range(len(seq_obj.children))):
            if not tmp_data.is_3d:
                type = obj.tbb.settings.telemac.z_name
                vertices = generate_mesh_data(tmp_data, mesh_is_3d=False, time_point=time_point, type=type)
            else:
                vertices = generate_mesh_data(tmp_data, mesh_is_3d=True, offset=id, time_point=time_point)

            set_new_shape_key(obj, vertices.flatten(), str(time_point), current_frame, time_point == end_time_point)


def generate_mesh_data(tmp_data: TBB_TelemacTemporaryData, mesh_is_3d: bool, offset: int = 0,
                       time_point: int = 0, type: str = 'BOTTOM') -> np.ndarray:
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

    if not mesh_is_3d and type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    # If file from a 3D simulation
    if mesh_is_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
        except Exception as warning:
            z_values = np.zeros((tmp_data.nb_vertices, 1))
            print(f"WARNING::generate_mesh_data: {warning}")

        # Ids from where to read data in the z_values array
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        vertices = np.hstack((tmp_data.vertices, z_values[start_id:end_id]))

    # If file from a 2D simulation
    else:
        if type == 'BOTTOM':
            possible_var_names = ["BOTTOM", "FOND"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
            except Exception as warning:
                z_values = np.zeros((tmp_data.nb_vertices, 1))
                print(f"WARNING::generate_mesh_data: {warning}")

            vertices = np.hstack((tmp_data.vertices, z_values))

        if type == 'WATER_DEPTH':
            possible_var_names = ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)

                # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                if var_name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                    bottom, var_name = tmp_data.get_data_from_possible_var_names(["BOTTOM", "FOND"], time_point)
                    z_values += bottom

            except Exception as warning:
                z_values = np.zeros((tmp_data.nb_vertices, 1))
                print(f"WARNING::generate_mesh_data: {warning}")

            vertices = np.hstack((tmp_data.vertices, z_values))

    return vertices


def generate_mesh_data_linear_interp(obj: Object, tmp_data: TBB_TelemacStreamingSequenceProperty,
                                     time_info: dict, offset: int = 0) -> np.ndarray:
    """
    Linearly interpolates the mesh of the given TELEMAC object.

    Args:
        obj (Object): object to interpolate
        tmp_data (TBB_TelemacStreamingSequenceProperty): temporary data
        time_info (dict): \
            { \
                "frame" (int): current frame, \
                "time_steps" (int): number of time steps between time points, \
                "l_time_point (int): left time point, \
                "l_frame" (int): frame which corresponds to the left time point, \
                "r_time_point (int): right time point, \
                "existing_time_point" (bool): if the time point is an existing time point \
            } \
        offset (int): corresponds to 'plane id' for meshes from 3D simulations. Defaults to 0.

    Raises:
        vertices_error: if something went wrong generating mesh data

    Returns:
        np.ndarray: vertices
    """

    # Get data from left time point
    try:
        l_vertices = generate_mesh_data(tmp_data, tmp_data.is_3d, offset=offset, time_point=time_info["l_time_point"],
                                        type=obj.tbb.settings.telemac.z_name)
    except Exception as vertices_error:
        raise vertices_error from vertices_error

    if not time_info["existing_time_point"]:
        # Get data from right time point
        try:
            r_vertices = generate_mesh_data(tmp_data, tmp_data.is_3d, offset=offset,
                                            time_point=time_info["r_time_point"], type=obj.tbb.settings.telemac.z_name)
        except Exception as vertices_error:
            raise vertices_error from vertices_error

        percentage = np.abs(time_info["frame"] - time_info["l_frame"]) / (time_info["time_steps"] + 1)

        return (l_vertices.T + (r_vertices.T - l_vertices.T) * percentage).T

    else:
        return l_vertices  # If it is an existing time point, no need to interpolate


def generate_base_objects(context: Context, time_point: int, name: str, import_point_data: bool = False,
                          point_data: str = "") -> list[Object]:
    """
    Generate objects using settings defined by the user. This function generates objects and vertex colors.

    If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth"). If the file
    is a 3D simulation, this will generate one object per plane.

    Args:
        context (Context): context
        time_point (int): time point from which to read data
        name (str): name of the objects
        import_point_data (bool, optional): import point data as vertex colors. Defaults to False.
        point_data (str, optional): JSON stringified deict of point data to import as vertex colors groups.\
                                    Defaults to "".

    Returns:
        list[Object]: generated object
    """

    settings = context.scene.tbb.settings.telemac
    tmp_data = settings.tmp_data

    objects = []
    if not tmp_data.is_3d:
        for type in ['BOTTOM', 'WATER_DEPTH']:
            vertices = generate_mesh_data(tmp_data, mesh_is_3d=False, time_point=time_point, type=type)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_" + type.lower())
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = type
            # Reset the scale without applying it
            obj.scale = [1.0, 1.0, 1.0]

            if import_point_data:
                res = prepare_telemac_point_data(obj.data, point_data, tmp_data, time_point, normalize='GLOBAL')
                generate_vertex_colors(obj.data, *res)

            objects.append(obj)
    else:
        for plane_id in range(tmp_data.nb_planes - 1, -1, -1):
            vertices = generate_mesh_data(tmp_data, mesh_is_3d=True, offset=plane_id, time_point=time_point)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_plane_" + str(plane_id))
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = str(plane_id)
            # Reset the scale without applying it
            obj.scale = [1.0, 1.0, 1.0]

            if import_point_data:
                res = prepare_telemac_point_data(obj.data, point_data, tmp_data, time_point,
                                                 mesh_is_3d=True, offset=plane_id, normalize='GLOBAL')
                generate_vertex_colors(obj.data, *res)

            objects.append(obj)

    return objects


def generate_preview_objects(context: Context, time_point: int = 0, name: str = "TBB_TELEMAC_preview") -> list[Object]:
    """
    Generate preview objects using settings defined by the user. Calls 'generate_base_objects'.

    This function also generate preview materials.

    Args:
        context (Context): context
        time_point (int, optional): time point of the preview. Defaults to 0.
        name (str, optional): name of the preview object. Defaults to "TBB_TELEMAC_preview".

    Returns:
        list[Object]: generated objects
    """

    settings = context.scene.tbb.settings.telemac
    tmp_data = settings.tmp_data
    collection = get_collection("TBB_TELEMAC", context)

    # Prepare the list of point data to preview
    prw_var_id = int(settings.preview_point_data)
    import_point_data = prw_var_id >= 0
    if import_point_data:
        vertex_colors_var_name = tmp_data.vars_info["names"][prw_var_id]
        point_data = [vertex_colors_var_name]
        # Generate vertex colors for all the variables
        # point_data = tmp_data.vars_info["names"]
        objects = generate_base_objects(context, time_point, name, import_point_data=import_point_data,
                                        point_data=point_data)
        for obj in objects:
            generate_preview_material(obj, vertex_colors_var_name)
    else:
        objects = generate_base_objects(context, time_point, name)

    # Add created objects to the right collection
    if tmp_data.is_3d:
        # Create a custom collection for 3D previews
        collection_3d = get_collection("TBB_TELEMAC_3D", context, link_to_scene=False)
        if collection_3d.name not in [col.name for col in collection.children]:
            collection.children.link(collection_3d)
        collection = collection_3d

    for obj in objects:
        # Check if not already in collection
        if collection.name not in [col.name for col in obj.users_collection]:
            collection.objects.link(obj)

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


def generate_telemac_streaming_sequence_obj(context: Context, name: str) -> Object:
    """
    Generate the base object for a TELEMAC 'streaming sequence'.

    Args:
        context (Context): context
        name (str): name of the sequence

    Returns:
        Object: generate object
    """

    settings = context.scene.tbb.settings.telemac
    collection = context.scene.collection

    # Create objects
    obj = bpy.data.objects.new(name=name + "_sequence", object_data=None)
    # Add temporary data to the dictionary of tmp_data in TBB_Object
    # WARNING: temporary data dictionary is also temporary (class attribute, not saved in the .blend file)
    obj.tbb.uid = str(time.time())
    obj.tbb.tmp_data[obj.tbb.uid] = TBB_TelemacTemporaryData()
    obj.tbb.tmp_data[obj.tbb.uid].update(settings.file_path)

    children = generate_base_objects(context, 0, name + "_sequence")

    for child in children:
        # Add object to the collection
        collection.objects.link(child)
        child.parent = obj

    # Normalize if needed (option set by the user)
    if settings.normalize_sequence_obj:
        normalize_objects(children, get_object_dimensions_from_mesh(children[0]))

    # Copy settings
    sequence = obj.tbb.settings.telemac.s_sequence

    sequence.normalize = settings.normalize_sequence_obj

    return obj


def prepare_telemac_point_data(obj: Object, tmp_data: TBB_TelemacTemporaryData, time_point: int,
                               offset: int = 0) -> tuple[list[dict], dict, int]:
    """
    Prepare point data for the 'generate_vertex_colors' function.

    Args:
        obj (Object): object
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_point (int): time point from which to read data
        offset (int, optional): if the mesh is from a 3D simulation, precise the offset in the data to read.\
            Defaults to 0.

    Returns:
        tuple[list[dict], dict, int]: vertex colors groups, data, nb_vertex_ids
    """

    # Prepare the mesh to loop over all its triangles
    mesh = obj.data
    if len(mesh.loop_triangles) == 0:
        mesh.calc_loop_triangles()

    vertex_ids = np.array([triangle.vertices for triangle in mesh.loop_triangles]).flatten()

    # Load point data information from JSON string
    settings = obj.tbb.settings
    point_data = json.loads(settings.point_data)

    # Format variables array
    variables = []
    for var, type in zip(point_data["names"], point_data["types"]):
        variables.append({"name": var, "type": type, "id": var})

    # Prepare data (remap)
    prepared_data = dict()
    for var, id in zip(variables, range(len(variables))):
        # Read data
        data = tmp_data.get_data_from_var_name(var["id"], time_point, output_shape='ROW')

        # Get right range of data in case of 3D simulation
        if tmp_data.is_3d:
            start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
            data = data[:, start_id:end_id]

        # Remap data
        if settings.remap_method == 'LOCAL':
            min, max = point_data["ranges"]["local"]["min"], point_data["ranges"]["local"]["max"]
            prepared_data[var["id"]] = remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max)
        elif settings.remap_method == 'GLOBAL':
            min, max = point_data["ranges"]["global"]["min"], point_data["ranges"]["global"]["max"]
            prepared_data[var["id"]] = remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max)
        else:
            prepared_data[var["id"]] = np.array(data)[vertex_ids]

    return generate_vertex_colors_groups(variables), prepared_data, len(vertex_ids)


def prepare_telemac_point_data_linear_interp(obj: Object, tmp_data: TBB_TelemacTemporaryData,
                                             time_info: dict, offset: int = 0) -> tuple[list[dict], dict, int]:
    """
    Prepare point data for linear interpolation of TELEMAC sequences.

    Args:
        obj (Object): object to interpolate
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_info (dict): \
            { \
                "frame" (int): current frame, \
                "time_steps" (int): number of time steps between time points, \
                "l_time_point (int): left time point, \
                "l_frame" (int): frame which corresponds to the left time point, \
                "r_time_point (int): right time point, \
                "existing_time_point" (bool): if the left time point is an existing time point \
            } \
        offset (int): corresponds to 'plane id' for meshes from 3D simulations. Defaults to 0.

    Raises:
        point_data_error: if something went wrong preparing point data

    Returns:
        tuple[list[dict], dict, int]: vertex colors groups, data, nb_vertex_ids
    """

    # Get data from left time point
    try:
        l_color_data = prepare_telemac_point_data(obj.data, tmp_data, time_info["l_time_point"], offset=offset)
    except Exception as point_data_error:
        raise point_data_error from point_data_error

    if not time_info["existing_time_point"]:
        # Get data from right time point
        try:
            r_color_data = prepare_telemac_point_data(obj.data, tmp_data, time_info["r_time_point"], offset=offset)
        except Exception as point_data_error:
            raise point_data_error from point_data_error

        percentage = np.abs(time_info["frame"] - time_info["l_frame"]) / (time_info["time_steps"] + 1)

        # Linearly interpolate
        color_data = l_color_data
        for id in color_data[1].keys():
            color_data[1][id] = l_color_data[1][id] + (r_color_data[1][id] - l_color_data[1][id]) * percentage

        return color_data

    else:
        return l_color_data  # If it is an existing time point, no need to interpolate


def set_new_shape_key(obj: Object, vertices: np.ndarray, name: str, frame: int, end: bool = False) -> None:
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

            if obj.tbb.is_streaming_sequence and sequence.update:
                # Get temporary data
                tmp_data = get_streaming_sequence_temporary_data(obj)
                if not tmp_data.is_ok():
                    try:
                        tmp_data.update(sequence.file_path)
                    except Exception as error:
                        print("ERROR::update_telemac_mesh_sequences: " + obj.name + ", " + str(error))

                # Compute limit
                limit = sequence.frame_start + sequence.anim_length
                if sequence.interpolate.type != 'NONE':
                    limit += (sequence.anim_length - 1) * sequence.interpolate.time_steps

                if frame >= sequence.frame_start and frame < limit:
                    start = time.time()

                    try:
                        objects = obj.children
                        for obj, id in zip(objects, range(len(objects))):
                            update_telemac_streaming_sequence_mesh(obj, sequence, frame, id, tmp_data)

                    except Exception as error:
                        print("ERROR::update_telemac_streaming_sequences: " + sequence.name + ", " + str(error))

                    print("Update::TELEMAC: " + sequence.name + ", " + "{:.4f}".format(time.time() - start) + "s")


def update_telemac_streaming_sequence_mesh(obj: Object, sequence: TBB_TelemacStreamingSequenceProperty,
                                           frame: int, id: int, tmp_data: TBB_TelemacTemporaryData) -> None:
    """
    Update the mesh of the given object from a TELEMAC 'streaming sequence' object.

    It also manages interpolation.

    Args:
        obj (Object): object from a TELEMAC sequence object
        settings (TBB_TelemacStreamingSequenceProperty): 'streaming sequence' settings
        frame (int): current frame
        id (int): id of the current object (used for meshes from 3D simulations, corresponds to the 'plane id')
        tmp_data (TBB_TelemacTemporaryData): temporary data

    Raises:
        tmp_data_error: if something went wrong loading the file
        mesh_error: if something went wrong generating mesh data
        point_data_error: if something went wrong generating vertex colors data
        ValueError: if the given time point does not exist
    """

    if sequence.interpolate.type == 'LINEAR':
        time_info = get_time_info_interp_streaming_sequence(frame, sequence.frame_start,
                                                            sequence.interpolate.time_steps)
    else:
        time_info = {"l_time_point": frame - sequence.frame_start, "existing_time_point": True}

    # Check if time point is ok
    time_point = time_info["l_time_point"]
    if time_point > tmp_data.nb_time_points:
        raise ValueError("time point '" + str(time_point) + "' does not exist. Available time\
                         points: " + str(tmp_data.nb_time_points))

    # Update mesh
    offset = id if tmp_data.is_3d else 0
    try:
        vertices = generate_mesh_data_linear_interp(obj, tmp_data, time_info, offset)
        obj = generate_object_from_data(vertices, tmp_data.faces, obj.name)
    except Exception as mesh_error:
        raise mesh_error from mesh_error

    # If import point data
    if obj.tbb.settings.import_point_data:
        # Remove old vertex colors
        while obj.data.vertex_colors:
            obj.data.vertex_colors.remove(obj.data.vertex_colors[0])

        # Update vertex colors data
        try:
            update_point_data_ranges(sequence, tmp_data, time_point)
            res = prepare_telemac_point_data_linear_interp(obj, tmp_data, time_info, offset=offset)
            generate_vertex_colors(obj.data, *res)
        except Exception as point_data_error:
            raise point_data_error from point_data_error


def update_point_data_ranges(obj: Object, tmp_data: TBB_TelemacTemporaryData,
                             time_point: int) -> None:
    """
    Compute and update point data ranges.

    Args:
        obj (Object): object
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_point (int): current time point to read
    """

    settings = obj.tbb.settings
    point_data = json.loads(settings.point_data)

    for var, id in zip(point_data["names"], range(len(point_data["names"]))):
        if settings.remap_method == 'LOCAL':
            # If local remap method, directly update value ranges
            data = tmp_data.get_data_from_var_name(var, time_point)
            point_data["ranges"][id]["local"]["min"] = np.min(data)
            point_data["ranges"][id]["local"]["max"] = np.max(data)
        elif settings.remap_method == 'GLOBAL':
            # Check if it already exists
            if point_data["ranges"][id]["global"]["min"] is None or point_data["ranges"][id]["global"]["max"] is None:
                min, max = tmp_data.get_var_value_range(var)
                point_data["ranges"][id]["global"]["min"] = min
                point_data["ranges"][id]["global"]["max"] = max

    obj.tbb.settings.point_data = json.dumps(point_data)
    print(point_data)


@persistent
def update_telemac_mesh_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'mesh sequence' objects.

    Args:
        scene (Scene): scene
    """

    if not scene.tbb.create_sequence_is_running:
        for obj in scene.objects:
            if obj.tbb.is_mesh_sequence and obj.tbb.settings.import_point_data:
                # Update children objects of 'mesh sequence'
                cumulated_time = 0.0

                # Get temporary data
                sequence = obj.tbb.settings.telemac.m_sequence
                tmp_data = obj.tbb.tmp_data[obj.tbb.uid]
                if not tmp_data.is_ok():
                    try:
                        tmp_data.update(sequence.file_path)
                    except Exception as error:
                        print("ERROR::update_telemac_mesh_sequences: " + obj.name + ", " + str(error))

                objects = obj.children
                for child, child_id in zip(objects, range(len(objects))):
                    time_info = get_time_info_interp_mesh_sequence(child, scene.frame_current)

                    if time_info is not None:
                        try:
                            start = time.time()
                            update_telemac_mesh_sequence_vertex_colors(child, child_id, sequence, time_info, tmp_data)
                            cumulated_time += time.time() - start
                        except Exception as error:
                            print("ERROR::update_telemac_mesh_sequences: " + child.name + ", " + str(error))

                if cumulated_time > 0.0:
                    print("Update::TELEMAC: " + obj.name + ", " + "{:.4f}".format(cumulated_time) + "s")


def update_telemac_mesh_sequence_vertex_colors(obj: Object, obj_id: int, sequence: TBB_TelemacMeshSequenceProperty,
                                               time_info: dict, tmp_data: TBB_TelemacTemporaryData) -> None:
    """
    Update vertex colors of the given TELEMAC 'mesh sequence' child object.

    Args:
        obj (Object): object to update
        obj_id (int): object id (child id)
        sequence (TBB_TelemacMeshSequenceProperty): mesh sequence settings
        time_info (dict): time information for interpolation

    Raises:
        tmp_data_error: if something went wrong updating temporary data
    """

    point_data = sequence.point_data.split(";")
    offset = obj_id if sequence.is_3d_simulation else 0

    # Remove existing vertex colors
    while obj.data.vertex_colors:
        obj.data.vertex_colors.remove(obj.data.vertex_colors[0])

    if time_info is not None:
        res = prepare_telemac_point_data_linear_interp(obj, tmp_data, time_info, point_data, offset=offset)
        generate_vertex_colors(obj.data, *res)


def get_time_info_interp_streaming_sequence(frame: int, frame_start: int, time_steps: int) -> dict:
    """
    Return necessary time information for 'streaming sequence' interpolation.

    Args:
        frame (int): current frame
        frame_start (int): start frame of the sequence
        time_steps (int): number of time steps between each time point

    Returns:
        dict: time information for interpolation

        .. code-block:: text

            Output:
            {
                "frame" (int): current frame,
                "time_steps" (int): time step between left and right time points,
                "l_time_point" (int): left time point,
                "l_frame" (int): corresponding frame for the left time point,
                "r_time_point" (int): right time point,
                "existing_time_point" (bool): indicate whether the left time point is an
                existing time point or not
            }
    """

    time_point = frame - frame_start

    if time_steps == 0:  # Existing time point
        return {
            "frame": frame,
            "time_steps": 0,
            "l_time_point": time_point,
            "l_frame": frame,
            "r_time_point": None,
            "existing_time_point": True
        }
    else:  # Interpolated time point
        info = compute_interp_time_info_streaming_sequence(time_point, time_steps)
        return {
            "frame": frame,
            "time_steps": time_steps,
            "l_time_point": info[0],
            "l_frame": frame_start + (time_steps + 1) * info[0],
            "r_time_point": info[1],
            "existing_time_point": info[2]
        }


def compute_interp_time_info_streaming_sequence(time_point: int, time_steps: int) -> tuple[int, int, bool]:
    """
    Compute time information for 'streaming sequence' interpolation.

    Args:
        time_point (int): current time point
        time_steps (int): number of time steps between each time point

    Returns:
        tuple[int, int, bool]: left time point, right time point, if left time point is an existing time point
    """

    modulo = time_point % (time_steps + 1)
    l_time_point = int((time_point - modulo) / (time_steps + 1))
    r_time_point = l_time_point + 1

    return l_time_point, r_time_point, modulo == 0


def get_time_info_interp_mesh_sequence(obj: Object, frame: int) -> Union[dict, None]:
    """
    Return necessary time information for 'mesh sequence' interpolation.

    Args:
        obj (Object): obj on which interpolate
        frame (int): current frame

    Returns:
        Union[dict, None]: time information for interpolation, None if current frame not in 'mesh sequence' time frame

        .. code-block:: text

            Output:
            {
                "frame" (int): current frame,
                "time_steps" (int): time step between left and right time points,
                "l_time_point" (int): left time point,
                "l_frame" (int): corresponding frame for the left time point,
                "r_time_point" (int): right time point,
                "existing_time_point" (bool): indicate whether the left time point is an
                existing time point or not
            }
    """

    # Get info from shape keys
    info = compute_interp_time_info_mesh_sequence(obj.data)

    # Make sure the time point is correct
    if info["frame_start"] <= frame <= info["frame_end"]:
        if info["state"] == 'BASIS':
            return {
                "frame": frame,
                "time_steps": 0,
                "l_time_point": info["start_offset"],
                "l_frame": info["frame_start"],
                "r_time_point": 1,
                "existing_time_point": True
            }
        elif info["state"] == 'EXISTING':
            return {
                "frame": frame,
                "time_steps": 0,
                "l_time_point": info["time_points"][0],
                "l_frame": info["frames"][0],
                "r_time_point": info["time_points"][0] + 1,
                "existing_time_point": True
            }
        elif info["state"] == 'INTERPOLATED':
            return {
                "frame": frame,
                "time_steps": np.abs(info["frames"][0] - info["frames"][1]) - 1,
                "l_time_point": info["time_points"][0],
                "l_frame": info["frames"][0],
                "r_time_point": info["time_points"][1],
                "existing_time_point": False
            }
        else:
            print("WARNING::get_time_info_interp_mesh_sequence: unknown state '" + str(info["state"]) + "'.")
            return None  # Unknown state

    else:
        return None  # Not in the right time frame


def compute_interp_time_info_mesh_sequence(blender_mesh: Mesh, threshold: float = 0.0001) -> dict:
    """
    Compute time information for 'streaming sequence' interpolation.

    .. code-block:: text

        Example of output:
        * TELEMAC mesh sequence: frame start = 12, anim length = 50.
        * Shape keys are linearly interpolated (2 time steps between each time point)
        * Current frame: 125

            Timeline
            Frames:     (12)⌄    (15)⌄                  (125)⌄                       (159)⌄
                            *  +  +  *  ...   *  +  +  *  +  +  *  +  +  *  ...  *  +  +  *
            Time points: (0)⌃     (1)⌃    (36)⌃    (37)⌃    (38)⌃    (39)⌃            (49)⌃

        Outputs:
        {
            "state": enum in ['BASIS', 'EXISTING', 'INTERPOLATED'] here 'INTERPOLATED',
            "start_offset": 0,
            "time_points": [37, 38],
            "ids": [123, 126],
            "frame_start": 12,
            "frame_end": 159
        }

    Args:
        blender_mesh (Mesh): mesh from which to get the information
        threshold (float, optional): threshold on the shape_key value. Defaults to 0.0001.

    Returns:
        dict: computed time information
    """

    fcurves = blender_mesh.shape_keys.animation_data.action.fcurves
    start_offset = int(blender_mesh.shape_keys.key_blocks[1].name) - 1
    output = {
        "state": "",
        "start_offset": start_offset,
        "time_points": [],
        "frames": [],
        "frame_start": fcurves[0].keyframe_points[0].co[0],
        "frame_end": fcurves[-1].keyframe_points[-1].co[0]
    }

    # Range starts from 1 because there is one more shape_key ('Basis')
    for fcurve, key_id in zip(fcurves, range(1, len(fcurves) + 1, 1)):
        if blender_mesh.shape_keys.key_blocks[key_id].value > threshold:
            output["frames"].append(fcurve.keyframe_points[1].co[0])
            output["time_points"].append(key_id + start_offset)

    # Check more precise info on time points
    if len(output["time_points"]) == 0:
        output["state"] = 'BASIS'
    elif len(output["time_points"]) == 1:
        # If the time point is not an existing time point (value is not 1.0 for the shape_key)
        if blender_mesh.shape_keys.key_blocks[output["time_points"][0] - start_offset].value != 1.0:
            # Check if it is between time points 0 and 1
            if output["time_points"][0] == 1:
                # First time point
                output["state"] = 'INTERPOLATED'
                output["time_points"].append(start_offset)
                output["frames"].append(fcurves[0].keyframe_points[0].co[0])
            else:
                # Last time point
                output["state"] = 'INTERPOLATED'
                output["time_points"].append(len(fcurves))
                output["frames"].append(fcurves[-1].keyframe_points[-1].co[0])
        else:
            output["state"] = 'EXISTING'
    elif len(output["time_points"]) == 2:
        output["state"] = 'INTERPOLATED'

    # Make sure it is always sorted
    output["frames"].sort()
    output["time_points"].sort()

    return output


def get_streaming_sequence_temporary_data(obj: Object) -> TBB_TelemacTemporaryData:
    """
    Get temporary data for streaming sequences from their uid.

    Args:
        obj (Object): streaming sequence object

    Returns:
        TBB_TelemacTemporaryData: temporary data
    """

    try:
        tmp_data = obj.tbb.tmp_data[obj.tbb.uid]
    except KeyError:
        obj.tbb.tmp_data[obj.tbb.uid] = TBB_TelemacTemporaryData()
        tmp_data = obj.tbb.tmp_data[obj.tbb.uid]

    return tmp_data
