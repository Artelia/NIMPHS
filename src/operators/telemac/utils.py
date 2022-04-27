# <pep8 compliant>
import bpy
from bpy.types import Context, Mesh, Object, Collection

import numpy as np

from ..utils import update_dynamic_props, generate_object_from_data, remap_array
from ...properties.telemac.Scene.settings import telemac_settings_dynamic_props
from ...properties.telemac.temporary_data import TBB_TelemacTemporaryData


def update_settings_dynamic_props(context: Context) -> None:
    """
    Update 'dynamic' settings of the main panel. It adapts the max values of properties in function of the imported file.

    :type context: Context
    """

    settings = context.scene.tbb_telemac_settings
    tmp_data = context.scene.tbb_telemac_tmp_data

    max_time_step = tmp_data.nb_time_points
    new_maxima = {
        "preview_time_point": max_time_step - 1,
        "start_time_point": max_time_step - 1,
        "end_time_point": max_time_step - 1,
    }
    update_dynamic_props(settings, new_maxima, telemac_settings_dynamic_props)


def generate_vertex_colors_name(var_id_groups: list, tmp_data: TBB_TelemacTemporaryData) -> str:
    """
    Generate the name of the vertex colors groups which correspond to the given list of ids.
    Example: 'FOND, VITESSE U, NONE' corresponds to: red channel = FOND, green channel = VITESS U, blue channel = NONE

    :param var_id_groups: ids of varibales names (from Serafin.nomvar)
    :type var_id_groups: list
    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :return: vertex colors name
    :rtype: str
    """

    name = ""
    for var_id, num in zip(var_id_groups, range(3)):
        if var_id != -1:
            name += tmp_data.variables_info["names"][var_id]
        else:
            name += "NONE"

        name += (", " if num != 2 else "")

    return name


def get_data_from_possible_var_names(tmp_data: TBB_TelemacTemporaryData,
                                     possible_var_names: list[str], time_point: int) -> np.ndarray:
    """
    Get data from the Serfain file and check for every possible given names. When one is found,
    return the associated data.

    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :param possible_var_names: variable names which could probably be defined in the Serafin file
    :type possible_var_names: list[str]
    :param time_point: time point to read data
    :type time_point: int
    :raises error: if an error occurred reading the Serafin file
    :raises NameError: if the possible names are not defined
    :return: read data
    :rtype: np.ndarray
    """

    z_values = None
    for var_name in possible_var_names:
        if z_values is None:
            try:
                z_values = tmp_data.get_data_from_var_name(var_name, time_point)
            except NameError:
                pass
            except Exception as error:
                raise error

        else:
            return z_values

    if z_values is None:
        raise NameError("ERROR::get_data_from_possible_var_names: undefined variables " + str(possible_var_names))
    else:
        return z_values


def generate_object(tmp_data: TBB_TelemacTemporaryData, mesh_is_3d: bool, offset: int = 0,
                    time_point: int = 0, type: str = 'BOTTOM', name: str = "TBB_TELEMAC_preview") -> Object:
    """
    Generate an object in function of the given settings and mesh data (2D / 3D).
    If the object already exsits, overwrite it.

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
    :param name: name of the object, defaults to "TBB_TELEMAC_preview"
    :type name: str, optional
    :raises NameError: if the given type is undefined
    :raises error: if an error occurred reading data
    :return: generated object
    :rtype: Object
    """

    if type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    # Manage 2D / 3D meshes
    if mesh_is_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
        except Exception as error:
            raise error

        start_id, end_id = offset * tmp_data.nb_vertices, offset * tmp_data.nb_vertices + tmp_data.nb_vertices
        vertices = np.hstack((tmp_data.vertices, z_values[start_id:end_id]))
    else:
        if type == 'BOTTOM':
            possible_var_names = ["BOTTOM", "FOND"]
            try:
                z_values = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

        if type == 'WATER_DEPTH':
            possible_var_names = ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"]
            try:
                z_values = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
            except Exception as error:
                raise error

            vertices = np.hstack((tmp_data.vertices, z_values))

        name += "_" + type.lower()

    blender_mesh, obj = generate_object_from_data(vertices, tmp_data.faces, name=name)

    # Set the object at the origin of the scene
    # obj.select_set(state=True, view_layer=context.view_layer)
    # bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    return obj


def generate_vertex_colors(tmp_data: TBB_TelemacTemporaryData, blender_mesh: Mesh,
                           list_point_data: str, time_point: int, mesh_is_3d: bool = False, offset: int = 0) -> None:
    """
    Generate vertex colors groups for each point data given in the list. The name given to the groups
    describe the content of the data contained in the groups.

    :param tmp_data: temporary data
    :type tmp_data: TBB_TelemacTemporaryData
    :param blender_mesh: mesh
    :type blender_mesh: Mesh
    :param list_point_data: list of point data to import as vertex colors groups
    :type list_point_data: str
    :param time_point: time point
    :type time_point: int
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
    :param apply: apply the rescale for each object in the collection
    :type apply: bool
    """

    if apply:
        # Deselect everything
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
    Get the dimensions of the object using its mesh.

    :param obj: object
    :type obj: Object
    :return: x, y, z dimensions
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
