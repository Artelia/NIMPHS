# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Mesh, Object, Context, Scene

import time
import numpy as np

from src.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from src.properties.telemac.telemac_interpolate import TBB_TelemacInterpolateProperty
from src.properties.telemac.Object.telemac_streaming_sequence import TBB_TelemacStreamingSequenceProperty
from src.operators.utils import (
    generate_object_from_data,
    remap_array,
    get_collection,
    generate_vertex_colors_groups,
    generate_vertex_colors,
    get_object_dimensions_from_mesh,
    normalize_objects)


def run_one_step_create_mesh_sequence_telemac(context: Context, current_frame: int, current_time_point: int,
                                              start_time_point: int, user_sequence_name: str):
    """
    Run one step of the 'create mesh sequence' for the TELEMAC module.

    Args:
        context (Context): context
        current_frame (int): current frame
        current_time_point (int): current time point
        start_time_point (int): start time point
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

            set_new_shape_key(obj, vertices.flatten(), str(time_point), current_frame)


def generate_mesh_data(tmp_data: TBB_TelemacTemporaryData, mesh_is_3d: bool, offset: int = 0,
                       time_point: int = 0, type: str = 'BOTTOM') -> np.ndarray:
    """
    Generate the mesh of the selected file. If the selected file is a 2D simulation, you can precise
    which part of the mesh you want ('BOTTOM' or 'WATER_DEPTH'). If the file is a 3D simulation, you can
    precise an offset for data reading (this offsets is somehow the id of the plane to generate)

    Args:
        tmp_data (TBB_TelemacTemporaryData): temporary data
        mesh_is_3d (bool): if the mesh is from a 3D simulation
        offset (int, optional): if the mesh is from a 3D simulation, precise the offset in the data to read.\
            Defaults to 0.
        time_point (int, optional): time point from which to read data. Defaults to 0.
        type (str, optional): type of the object, enum in ['BOTTOM', 'WATER_DEPTH']. Defaults to 'BOTTOM'.

    Raises:
        NameError: if the given type is undefined
        error: if an error occurred reading data

    Returns:
        np.ndarray: vertices of the mesh, shape is (number_of_vertices, 3)
    """

    if not mesh_is_3d and type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    # Manage 2D / 3D meshes
    if mesh_is_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
        except Exception as error:
            raise error

        # Ids from where to read data in the z_values array
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        vertices = np.hstack((tmp_data.vertices, z_values[start_id:end_id]))
    else:
        if type == 'BOTTOM':
            possible_var_names = ["BOTTOM", "FOND"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)
            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

        if type == 'WATER_DEPTH':
            possible_var_names = ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"]
            try:
                z_values, var_name = tmp_data.get_data_from_possible_var_names(possible_var_names, time_point)

                # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                if var_name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                    bottom, var_name = tmp_data.get_data_from_possible_var_names(["BOTTOM", "FOND"], time_point)
                    z_values += bottom

            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

    # TODO: where to add this option? (Set object's origin to center of the world)
    # Set the object at the origin of the scene
    # obj.select_set(state=True, view_layer=context.view_layer)
    # bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    return vertices


def generate_base_objects(context: Context, time_point: int, name: str, import_point_data: bool = False,
                          list_point_data: list[str] = [""]) -> list[Object]:
    """
    Generate objects using settings defined by the user. This function generates objects and vertex colors.
    If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth"). If the file
    is a 3D simulation, this will generate one object per plane.

    Args:
        context (Context): context
        time_point (int): time point from which to read data
        name (str): name of the objects
        import_point_data (bool, optional): import point data as vertex colors. Defaults to False.
        list_point_data (list[str], optional): list of point data to import as vertex colors groups. Defaults to [""].

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
                res = prepare_telemac_point_data(obj.data, list_point_data, tmp_data, time_point, normalize='GLOBAL')
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
                res = prepare_telemac_point_data(obj.data, list_point_data, tmp_data, time_point,
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
                                        list_point_data=point_data)
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
    seq_obj = bpy.data.objects.new(name=name + "_sequence", object_data=None)
    objects = generate_base_objects(context, 0, name + "_sequence")

    for obj in objects:
        # Add 'Basis' shape key
        # obj.shape_key_add(name="Basis", from_mix=False)

        # Add the object to the collection
        collection.objects.link(obj)
        obj.parent = seq_obj

    # Normalize if needed (option set by the user)
    if settings.normalize_sequence_obj:
        normalize_objects(objects, get_object_dimensions_from_mesh(objects[0]))

    # Copy settings
    seq_settings = seq_obj.tbb.settings.telemac.streaming_sequence

    seq_settings.normalize = settings.normalize_sequence_obj

    return seq_obj


def prepare_telemac_point_data(blender_mesh: Mesh, list_point_data: list[str], tmp_data: TBB_TelemacTemporaryData,
                               time_point: int, mesh_is_3d: bool = False, offset: int = 0,
                               normalize: str = 'LOCAL') -> tuple[list[dict], dict, int]:
    """
    Prepare point data for the 'generate_vertex_colors' function.

    Args:
        blender_mesh (Mesh): mesh on which to add vertex colors
        list_point_data (list[str]): list of point data
        tmp_data (TBB_TelemacTemporaryData): temporary data
        time_point (int): time point from which to read data
        mesh_is_3d (bool, optional): if the mesh is from a 3D simulation. Defaults to False.
        offset (int, optional): if the mesh is from a 3D simulation, precise the offset in the data to read.\
            Defaults to 0.
        normalize (str, optional): normalize vertex colors, enum in ['LOCAL', 'GLOBAL']. Defaults to 'LOCAL'.

    Returns:
        tuple[list[dict], dict, int]: vertex colors groups, data, nb_vertex_ids
    """

    # Prepare the mesh to loop over all its triangles
    if len(blender_mesh.loop_triangles) == 0:
        blender_mesh.calc_loop_triangles()

    vertex_ids = np.array([triangle.vertices for triangle in blender_mesh.loop_triangles]).flatten()

    # Filter elements which evaluates to 'False', ex: ''
    list_point_data = list(filter(None, list_point_data))
    # Filter variables if they do not exist and build to output
    filtered_variables = []
    for var_name in list_point_data:
        for name, id in zip(tmp_data.file.nomvar, range(tmp_data.nb_vars)):
            if var_name in name:
                filtered_variables.append({"name": var_name, "type": 'SCALAR', "id": id})

    # Prepare data
    prepared_data, data = dict(), tmp_data.read(time_point)

    if mesh_is_3d:
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        data = data[:, start_id:end_id]

    for var in filtered_variables:
        if normalize == 'GLOBAL':
            min, max = tmp_data.get_var_value_range(var["id"])
        elif normalize == 'LOCAL':
            min, max = np.min(data[var["id"]]), np.max(data[var["id"]])

        prepared_data[var["id"]] = remap_array(np.array(data[var["id"]])[vertex_ids], in_min=min, in_max=max)

    return generate_vertex_colors_groups(filtered_variables), prepared_data, len(vertex_ids)


def set_new_shape_key(obj: Object, vertices: np.ndarray, name: str, frame: int) -> None:
    """
    Add a shape key to the object using the given vertices. It also set a keyframe with value = 1.0 at the given frame
    and add keyframes at value = 0.0 around the frame (-1 and +1).

    Args:
        obj (Object): object to receive the new shape key
        vertices (np.ndarray): new vertices values
        name (str): name of the shape key
        frame (int): the frame on which the keyframe is inserted
    """

    obj.data.vertices.foreach_set("co", vertices.flatten())

    # Add a shape key
    block = obj.shape_key_add(name=name, from_mix=False)
    block.value = 1.0
    # Keyframe the new shape key
    block.keyframe_insert("value", frame=frame, index=-1)
    block.value = 0.0
    block.keyframe_insert("value", frame=frame - 1, index=-1)
    block.keyframe_insert("value", frame=frame + 1, index=-1)


@persistent
def update_telemac_streaming_sequences(scene: Scene) -> None:
    """
    App handler appened to the frame_change_pre handlers.
    Updates all the TELEMAC 'streaming sequences' of the scene.

    Args:
        scene (Scene): scene
    """

    frame = scene.frame_current

    if not scene.tbb.create_sequence_is_running:
        for obj in scene.objects:
            settings = obj.tbb.settings.telemac.streaming_sequence

            if obj.tbb.is_streaming_sequence and settings.update:
                time_point = frame - settings.frame_start
                interpolate = settings.interpolate
                point_data = settings.list_point_data.split(";")

                # Compute limit
                limit = settings.anim_length
                if interpolate.type != 'NONE':
                    limit = limit * (interpolate.time_steps + 1) - interpolate.time_steps

                if time_point >= 0 and time_point < limit:
                    start = time.time()
                    try:
                        objects = obj.children
                        for obj, id in zip(objects, range(len(objects))):
                            update_telemac_streaming_sequence_mesh(obj, settings, time_point, id, interpolate,
                                                                   point_data)

                    except Exception as error:
                        print("ERROR::update_telemac_streaming_sequences: " + settings.name + ", " + str(error))

                    print("Update::TELEMAC: " + settings.name + ", " + "{:.4f}".format(time.time() - start) + "s")


def update_telemac_streaming_sequence_mesh(obj: Object, settings: TBB_TelemacStreamingSequenceProperty,
                                           time_point: int, id: int, interpolate: TBB_TelemacInterpolateProperty, point_data: list[str]) -> None:
    """
    Update the mesh of the given object from a TELEMAC sequence object.

    Args:
        obj (Object): object from a TELEMAC sequence object
        settings (TBB_TelemacStreamingSequenceProperty): 'streaming sequence' settings
        time_point (int): time point
        id (int): id of the current object (used for meshes from 3D simulations, corresponds to the 'plane id')
        interpolate (TBB_TelemacInterpolateProperty): interpolation settings
        point_data (list[str]): list of point data to import as vertex colors

    Raises:
        tmp_data_error: if something went wrong loading the file
        vertices_error: if something went wrong generating mesh data
        point_data_error: if something went wrong generating vertex colors data
        ValueError: if the given time point does not exist
    """

    # Check if tmp_data is loaded
    tmp_data = settings.tmp_data
    if not settings.tmp_data.is_ok():
        try:
            settings.tmp_data.update(settings.file_path)
        except Exception as tmp_data_error:
            raise tmp_data_error from tmp_data_error

    # Filter the given list
    point_data = list(filter(None, point_data))
    import_point_data = len(point_data) > 0

    # Compute left time point if interpolate option is 'on'
    existing_time_point = False
    if interpolate.type != 'NONE':
        time_point_offset = interpolate.time_steps + 1
        modulo = time_point % time_point_offset
        l_time_point = int((time_point - modulo) / time_point_offset)
        r_time_point = l_time_point + 1
        if modulo == 0:
            existing_time_point = True
    else:
        l_time_point = time_point
        existing_time_point = True

    # Check if time poit is ok
    if l_time_point > tmp_data.nb_time_points:
        raise ValueError("time point '" + str(l_time_point) + "' does not exist. Available time points: " +
                         str(tmp_data.nb_time_points))

    print(l_time_point)

    # Generate mesh
    offset = id if tmp_data.is_3d else 0  # For meshes from 3D simulation
    try:
        l_vertices = generate_mesh_data(tmp_data, tmp_data.is_3d, offset=offset, time_point=l_time_point,
                                        type=obj.tbb.settings.telemac.z_name)
    except Exception as vertices_error:
        raise vertices_error from vertices_error

    # Generate vertex colors data
    if import_point_data:
        try:
            l_color_data = prepare_telemac_point_data(obj.data, point_data, tmp_data, l_time_point,
                                                      mesh_is_3d=tmp_data.is_3d, offset=offset, normalize='GLOBAL')
        except Exception as point_data_error:
            raise point_data_error from point_data_error

    # Interpolate mesh and vertex colors data
    if not existing_time_point and l_time_point < tmp_data.nb_time_points and interpolate.type == 'LINEAR':
        # How much to add to l_vertices from the
        percentage = (time_point % time_point_offset) / time_point_offset

        # Interpolate vertices
        try:
            r_vertices = generate_mesh_data(tmp_data, tmp_data.is_3d, offset=offset, time_point=r_time_point,
                                            type=obj.tbb.settings.telemac.z_name)
        except Exception as vertices_error:
            raise vertices_error from vertices_error

        vertices = (l_vertices.T + (r_vertices.T - l_vertices.T) * percentage).T

        # Interpolate vertex colors data
        if import_point_data:
            r_color_data = prepare_telemac_point_data(obj.data, point_data, tmp_data, r_time_point,
                                                      mesh_is_3d=tmp_data.is_3d, offset=offset, normalize='GLOBAL')
            color_data = l_color_data
            for id in color_data[1].keys():
                color_data[1][id] = l_color_data[1][id] + (r_color_data[1][id] - l_color_data[1][id]) * percentage
    else:
        vertices = l_vertices
        if import_point_data:
            color_data = l_color_data

    # Update mesh
    obj = generate_object_from_data(vertices, tmp_data.faces, obj.name)

    # Remove old vertex colors
    if import_point_data:
        while obj.data.vertex_colors:
            obj.data.vertex_colors.remove(obj.data.vertex_colors[0])
        # Update vertex colors data
        generate_vertex_colors(obj.data, *color_data)
