# <pep8 compliant>
import bpy
from bpy.types import Context, Mesh, Object

import numpy as np

from ..utils import update_dynamic_props, generate_object_from_data
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


def generate_object(tmp_data: TBB_TelemacTemporaryData, context: Context, settings, rescale: str = 'NONE',
                    time_point: int = 0, type: str = 'BOTTOM', name: str = "TBB_TELEMAC_preview") -> Object:
    """
    Generate an object in function of the given settings and mesh data (2D / 3D).
    If the object already exsits, overwrite it.

    :type tmp_data: TBB_TelemacTemporaryData
    :type context: Context
    :param time_point: custom time point, defaults to 0
    :type time_point: int, optional
    :param rescale: rescale the object, enum in ['NONE', 'NORMALIZE', 'RESET']
    :type rescale: bool
    :param type: type of the object, enum in ['BOTTOM', 'WATER_DEPTH'], defaults to 'BOTTOM'
    :type type: str
    :param name: name of the object, defaults to 'TBB_TELEMAC_preview'
    :type name: str
    :return: the generated object
    :rtype: Object
    """

    if type not in ['BOTTOM', 'WATER_DEPTH']:
        raise NameError("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")

    mesh_id_3d = tmp_data.nb_planes > 1

    # Manage 2D / 3D meshes
    if mesh_id_3d:
        possible_var_names = ["ELEVATION Z", "COTE Z"]
        try:
            z_values = get_data_from_possible_var_names(tmp_data, possible_var_names, time_point)
        except Exception as error:
            raise error

        vertices = np.hstack((tmp_data.vertices, z_values))
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

    blender_mesh, obj = generate_object_from_data(vertices, tmp_data.faces, context, name + "_" + type.lower())
    # Set the object at the origin of the scene
    obj.select_set(state=True, view_layer=context.view_layer)
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    if rescale != 'NONE':
        if rescale == 'NORMALIZE':
            normalize_object(obj, settings.preview_obj_dimensions, mesh_id_3d)
        elif rescale == 'RESET':
            rescale_object(obj, settings.preview_obj_dimensions, mesh_id_3d)

    return obj


def generate_vertex_colors(tmp_data: TBB_TelemacTemporaryData, blender_mesh: Mesh,
                           list_point_data: str, time_point: int) -> None:
    """
    Generate vertex color groups for each point data given in the list. The name given to the groups
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
                max_value = np.max(np.array(data[var_id])[vertex_ids])  # Normalize values
                array = np.array(data[var_id])[vertex_ids]
                if max_value > np.finfo(np.float).eps:
                    colors.append(array / max_value)
                else:
                    colors.append(array)
            else:
                colors.append(zeros)

        # Add ones for alpha channel
        colors.append(ones)

        # Reshape data
        colors = np.array(colors).T

        colors = colors.flatten()
        vertex_colors.data.foreach_set("color", colors)


def normalize_object(obj: Object, dimensions: list[float], mesh_3d: bool = False) -> None:
    """
    Rescale the object so its coordinates are now in the range [-1;1].

    :param obj: object to normalize
    :type obj: Object
    :param dimensions: original dimensions of the object
    :type dimensions: list[float]
    :param mesh_3d: true if this mesh is from a 3D simulation, defaults to False
    :type mesh_3d: bool, optional
    """

    ratio = dimensions[0] / dimensions[1]
    scale_x, scale_y = 1.0 if ratio > 1.0 else 1.0 / ratio, 1.0 if ratio < 1.0 else 1.0 / ratio
    scale_z = 1.0 / dimensions[2] if dimensions[2] > np.finfo(np.float).eps else 1.0
    rescale_object(obj, [scale_x, scale_y, scale_z], mesh_3d)


def rescale_object(obj: Object, dimensions: list[float], mesh_3d: bool = False) -> None:
    """
    Rescale an object using the given dimensions.

    :param obj: object to rescale
    :type obj: Object
    :param dimensions: target dimensions
    :type dimensions: list[float]
    :param mesh_3d: true if this mesh is from a 3D simulation, defaults to False
    :type mesh_3d: bool, optional
    """

    obj.dimensions[0] = dimensions[0]
    # Weird but we have to do 'transform_apply' each time we modify the dimensions attribute
    bpy.ops.object.transform_apply(location=False)
    obj.dimensions[1] = dimensions[1]
    bpy.ops.object.transform_apply(location=False)
    if mesh_3d:
        obj.dimensions[2] = dimensions[2]
        bpy.ops.object.transform_apply(location=False)
