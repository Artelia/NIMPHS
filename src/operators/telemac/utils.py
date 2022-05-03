# <pep8 compliant>
import bpy
from bpy.types import Mesh, Object, Collection, Context

import numpy as np

from ..utils import generate_object_from_data, remap_array, get_collection
from ...properties.telemac.temporary_data import TBB_TelemacTemporaryData


def generate_vertex_colors_name(var_id_groups: list[int], tmp_data: TBB_TelemacTemporaryData) -> str:
    """
    Generate the name of the vertex colors groups which correspond to the given list of ids.
    Example: 'FOND, VITESSE U, NONE' corresponds to: red channel = FOND, green channel = VITESS U, blue channel = NONE

    :param var_id_groups: ids of varibales names (from Serafin.nomvar)
    :type var_id_groups: list[int]
    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :return: vertex colors name
    :rtype: str
    """

    name = ""
    for var_id, num in zip(var_id_groups, range(3)):
        if var_id != -1:
            name += tmp_data.vars_info["names"][var_id]
        else:
            name += "NONE"

        name += (", " if num != 2 else "")

    return name


def get_data_from_possible_var_names(tmp_data: TBB_TelemacTemporaryData,
                                     possible_var_names: list[str], time_point: int) -> tuple[np.ndarray, str]:
    """
    Get data from the Serafin file (.slf) and check for every possible given names. When one is found,
    return the associated data.

    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :param possible_var_names: variable names which could probably be defined in the Serafin file
    :type possible_var_names: list[str]
    :param time_point: time point to read data
    :type time_point: int
    :raises error: if an error occurred reading the Serafin file
    :raises NameError: if the possible names are not defined
    :return: data, var_name
    :rtype: tuple[np.ndarray, str]
    """

    z_values = None
    for var_name in possible_var_names:
        try:
            z_values = tmp_data.get_data_from_var_name(var_name, time_point)
        except NameError:
            pass
        except Exception as error:
            raise error

        if z_values is not None:
            return z_values, var_name

    if z_values is None:
        raise NameError("ERROR::get_data_from_possible_var_names: undefined variables " + str(possible_var_names))
    else:
        return z_values, var_name


def generate_mesh(tmp_data: TBB_TelemacTemporaryData, mesh_is_3d: bool, offset: int = 0,
                  time_point: int = 0, type: str = 'BOTTOM') -> np.ndarray:
    """
    Generate the mesh of the selected file. If the selected file is a 2D simulation, you can precise
    which part of the mesh you want ('BOTTOM' or 'WATER_DEPTH'). If the file is a 3D simulation, you can
    precise an offset for data reading (this offsets is somehow the id of the plane to generate)

    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :param mesh_is_3d: if the mesh is a 3D simulation
    :type mesh_is_3d: bool
    :param offset: if the mesh is a 3D simulation, precise the offset in the data to read
    :type offset: int
    :param time_point: time point to read
    :type time_point: int, optional
    :param type: type of the object, enum in ['BOTTOM', 'WATER_DEPTH'], defaults to 'BOTTOM'
    :type type: str, optional
    :raises NameError: if the given type is undefined
    :raises error: if an error occurred reading data
    :return: vertices of the mesh
    :rtype: np.ndarray
    """

    if not mesh_is_3d and type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    # Manage 2D / 3D meshes
    if mesh_is_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values, var_name = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
        except Exception as error:
            raise error

        # Ids from where to read data in the z_values array
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        vertices = np.hstack((tmp_data.vertices, z_values[start_id:end_id]))
    else:
        if type == 'BOTTOM':
            possible_var_names = ["BOTTOM", "FOND"]
            try:
                z_values, var_name = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

        if type == 'WATER_DEPTH':
            possible_var_names = ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"]
            try:
                z_values, var_name = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)

                # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                if var_name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                    bottom, var_name = get_data_from_possible_var_names(tmp_data, ["BOTTOM", "FOND"], time_point)
                    z_values += bottom

            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

    # TODO: where to add this option? (Set object's origin to center of the world)
    # Set the object at the origin of the scene
    # obj.select_set(state=True, view_layer=context.view_layer)
    # bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    return vertices


def generate_vertex_colors(tmp_data: TBB_TelemacTemporaryData, blender_mesh: Mesh,
                           list_point_data: list[str], time_point: int, mesh_is_3d: bool = False, offset: int = 0) -> None:
    """
    Generate vertex colors groups for each point data given in the list. The name given to the groups
    describe the content of the data contained in the groups.

    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :param blender_mesh: mesh
    :type blender_mesh: Mesh
    :param list_point_data: list of point data to import as vertex colors groups
    :type list_point_data: list[str]
    :param time_point: time point to read data
    :type time_point: int
    :param mesh_is_3d: precise if the mesh is from a 3D simulation
    :type mesh_is_3d: bool
    :param offset: for a mesh from a 3D simulation, precise the offset to read data
    :type offset: int
    """

    # Prepare the mesh to loop over all its triangles
    if len(blender_mesh.loop_triangles) == 0:
        blender_mesh.calc_loop_triangles()
    # triangle_ids = np.arange(0, len(blender_mesh.loop_triangles), 1)
    vertex_ids = np.array([triangle.vertices for triangle in blender_mesh.loop_triangles]).flatten()

    # Filter variables
    filtered_variables_indices = []
    for var_name in list_point_data:
        for name, id in zip(tmp_data.file.nomvar, range(tmp_data.nb_vars)):
            if var_name in name:
                filtered_variables_indices.append(id)

    data = tmp_data.read(time_point)
    if mesh_is_3d:
        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        data = data[:, start_id:end_id]

    ones = np.ones((len(vertex_ids),))
    zeros = np.zeros((len(vertex_ids),))

    # Add '-1' to the array if it is not a multiple of 3
    res = len(filtered_variables_indices) % 3
    if res != 0:
        filtered_variables_indices += [-1] * (3 - res)
    nb_groups = int(len(filtered_variables_indices) / 3)

    # Clear vertex colors groups
    while blender_mesh.vertex_colors:
        blender_mesh.vertex_colors.remove(blender_mesh.vertex_colors[0])

    for var_id_groups in np.array(filtered_variables_indices).reshape(nb_groups, 3):
        name = generate_vertex_colors_name(var_id_groups, tmp_data)
        vertex_colors = blender_mesh.vertex_colors.new(name=name, do_init=True)

        colors = []
        for var_id in var_id_groups:
            if var_id != -1:
                min, max = tmp_data.get_var_value_range(var_id)
                colors_data = remap_array(np.array(data[var_id])[vertex_ids], in_min=min, in_max=max)
                colors.append(colors_data)
            else:
                colors.append(zeros)

        # Add ones for alpha channel
        colors.append(ones)

        # Reshape data
        colors = np.array(colors).T

        colors = colors.flatten()
        vertex_colors.data.foreach_set("color", colors)


def generate_preview_material(obj: Object, var_name: str, name: str = "TBB_TELEMAC_preview_material") -> None:
    """
    Generate the preview material (if not generated yet). Update it otherwise (with the new variable).
    This generates the following node tree: 'Vertex color'[color] >>> [image]'Separate RBG'[R, G, B] >>> [color]'Principled BSDF'

    :param obj: preview object
    :type obj: Object
    :param var_name: name of the variable to preview
    :type var_name: str
    :param name: name of the material, defaults to "TBB_TELEMAC_preview_material"
    :type name: str, optional
    :raises NameError: if the variable is not found in the vertex colors groups
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


def normalize_objects(objects: list[Object], dimensions: list[float]) -> None:
    """
    Rescale the given list of objects so coordinates of all the meshes are now in the range [-1;1].

    :param collection: objects to normalize
    :type collection: list[Object]
    :param dimensions: original dimensions
    :type dimensions: list[float]
    """

    factor = 1.0 / np.max(dimensions)
    rescale_objects(objects, [factor, factor, factor])


def rescale_objects(objects: list[Object], dimensions: list[float], apply: bool = False) -> None:
    """
    Resize a collection using the given dimensions.

    :param collection: objects to normalize
    :type collection: list[Object]
    :param dimensions: target dimensions
    :type dimensions: list[float]
    :param apply: apply the rescale for each object in the given list
    :type apply: bool
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


def get_object_dimensions_from_mesh(obj: Object) -> list[float]:
    """
    Compute the dimensions of the object from its mesh.

    :param obj: object
    :type obj: Object
    :return: (x, y, z) dimensions
    :rtype: list[float]
    """

    dimensions = []
    vertices = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
    obj.data.vertices.foreach_get("co", vertices)
    vertices = vertices.reshape((int(len(vertices) / 3)), 3)
    dimensions.append(np.max(vertices[:, 0]) - np.min(vertices[:, 0]))
    dimensions.append(np.max(vertices[:, 1]) - np.min(vertices[:, 1]))
    dimensions.append(np.max(vertices[:, 2]) - np.min(vertices[:, 2]))
    return dimensions


def set_new_shape_key(obj: Object, vertices: np.ndarray, name: str, frame: int) -> None:
    """
    Add a shape key to the object using the given vertices. It also set a keyframe with value = 1.0 at the given frame
    and add keyframes at value = 0.0 around the given frame (-1 and +1).

    :param obj: object to receive the new shape key
    :type obj: Object
    :param vertices: new vertices
    :type vertices: np.ndarray
    :param name: name of the shape key
    :type name: str
    :param frame: the frame on which the keyframe is inserted
    :type frame: int
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


def generate_preview_objects(context: Context, time_point: int = 0, name: str = "TBB_TELEMAC_preview") -> list[Object]:
    """
    Generate preview objects using settings defined by the user. Calls 'generate_base_objects'.

    :type context: Context
    :param time_point: time point of the preview, defaults to 0
    :type time_point: int, optional
    :param name: name of the preview object, defaults to "TBB_TELEMAC_preview"
    :type name: str, optional
    :return: generated objects
    :rtype: list[Object]
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
                                        vertex_colors_var_name=vertex_colors_var_name, point_data=point_data)
    else:
        objects = generate_base_objects(context, time_point, name)

    if tmp_data.is_3d:
        # Create a custom collection for 3D previews
        collection_3d = get_collection("TBB_TELEMAC_3D", context, link_to_scene=False)
        if collection_3d.name not in [col.name for col in collection.children]:
            collection.children.link(collection_3d)
        collection = collection_3d

    # Add new objects to the collection
    for obj in objects:
        if collection.name not in [col.name for col in obj.users_collection]:
            collection.objects.link(obj)

    return objects


def generate_base_objects(context: Context, time_point: int, name: str, import_point_data: bool = False,
                          vertex_colors_var_name: str = "", point_data: list[str] = [""]) -> list[Object]:
    """
    Generate objects using settings defined by the user. This function generates objects,
    vertex colors and preview materials.

    :type context: Context
    :param time_point: time point
    :type time_point: int
    :param name: name of the objects
    :type name: str
    :param import_point_data: import point data as vertex colors, defaults to False
    :type import_point_data: bool, optional
    :param vertex_colors_var_name: name given to the vertex colors groups, defaults to ""
    :type vertex_colors_var_name: str, optional
    :param point_data: list of point data to import as vertex colors groups, defaults to [""]
    :type point_data: list[str], optional
    :return: generated objects
    :rtype: list[Object]
    """

    settings = context.scene.tbb.settings.telemac
    tmp_data = settings.tmp_data

    objects = []
    if not tmp_data.is_3d:
        for type in ['BOTTOM', 'WATER_DEPTH']:
            vertices = generate_mesh(tmp_data, mesh_is_3d=False, time_point=time_point, type=type)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_" + type.lower())
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = type
            # Reset the scale without applying it
            obj.scale = [1.0, 1.0, 1.0]

            if import_point_data:
                generate_vertex_colors(tmp_data, obj.data, point_data, time_point)
                generate_preview_material(obj, vertex_colors_var_name)

            objects.append(obj)
    else:
        for plane_id in range(tmp_data.nb_planes - 1, -1, -1):
            vertices = generate_mesh(tmp_data, mesh_is_3d=True, offset=plane_id, time_point=time_point)
            obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_plane_" + str(plane_id))
            # Save the name of the variable used for 'z-values' of the vertices
            obj.tbb.settings.telemac.z_name = str(plane_id)
            # Reset the scale without applying it
            obj.scale = [1.0, 1.0, 1.0]

            if import_point_data:
                generate_vertex_colors(tmp_data, obj.data, point_data, time_point, mesh_is_3d=True, offset=plane_id)
                generate_preview_material(obj, vertex_colors_var_name)

            objects.append(obj)

    return objects
