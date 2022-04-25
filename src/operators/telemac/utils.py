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
    | Generate the name of the vertex colors group which correspond do the given list of ids.
    | Example: 'FOND, VITESS U, NONE' corresponds to: red channel = FOND, green channel = VITESS U, blue channel = NONE

    :param var_id_groups: ids of varibales names (Serafin.nomvar array)
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


def generate_object(tmp_data: TBB_TelemacTemporaryData, context: Context, settings, rescale: str = 'NONE',
                    time_point: int = 0, name: str = "TBB_TELEMAC_preview") -> Object:
    """
    Generate an object in function of the given settings and mesh data (3D / 2D).
    If the object already exsits, overwrite it.

    :type tmp_data: TBB_TelemacTemporaryData
    :type context: Context
    :param time_point: custom time point, defaults to 0
    :type time_point: int, optional
    :param rescale: rescale the object, enum in ['NONE', 'NORMALIZE', 'RESET']
    :type rescale: bool
    :param name: name of the object, defaults to 'TBB_TELEMAC_preview'
    :type name: str
    :return: the generated object
    :rtype: Object
    """

    # Read data at the given time point
    try:
        data = tmp_data.read(time_point)
    except Exception as error:
        raise error

    mesh_id_3d = tmp_data.nb_planes > 1

    # Manage 2D / 3D meshes
    if mesh_id_3d:
        # data[0] is 'COTE Z'
        z_values = np.array(data[0]).reshape(data[0].shape[0], 1)
        vertices = np.hstack((tmp_data.vertices, z_values))
    else:
        vertices = np.hstack((tmp_data.vertices, np.zeros((tmp_data.nb_vertices, 1))))

    blender_mesh, obj = generate_object_from_data(vertices, tmp_data.faces, context, name)
    # Set the object at the origin of the scene
    obj.select_set(state=True, view_layer=context.view_layer)
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

    if rescale != 'NONE':
        if rescale == 'NORMALIZE':
            normalize_object(obj, settings.preview_obj_dimensions, mesh_id_3d)
        elif rescale == 'RESET':
            rescale_object(obj, settings.preview_obj_dimensions, mesh_id_3d)

    return obj


def normalize_object(obj: Object, dimensions: list[float], mesh_3d: bool = False) -> None:
    ratio = dimensions[0] / dimensions[1]
    scale_x, scale_y = 1.0 if ratio > 1.0 else 1.0 / ratio, 1.0 if ratio < 1.0 else 1.0 / ratio
    scale_z = 1.0 / dimensions[2] if dimensions[2] > np.finfo(np.float).eps else 1.0
    rescale_object(obj, [scale_x, scale_y, scale_z], mesh_3d)


def rescale_object(obj: Object, dimensions: list[float], mesh_3d: bool = False) -> None:
    obj.dimensions[0] = dimensions[0]
    # Weird but we have to do 'transform_apply' each time we modify the dimensions attribute
    bpy.ops.object.transform_apply(location=False)
    obj.dimensions[1] = dimensions[1]
    bpy.ops.object.transform_apply(location=False)
    if mesh_3d:
        obj.dimensions[2] = dimensions[2]
        bpy.ops.object.transform_apply(location=False)


def generate_vertex_colors(tmp_data: TBB_TelemacTemporaryData, blender_mesh: Mesh,
                           list_point_data: str, time_point: int) -> None:
    """
    Generate vertex color groups for each point data given in the list. The name given to the groups
    describe the content of the data contained in the groups.

    :param tmp_data: _description_
    :type tmp_data: TBB_TelemacTemporaryData
    :param blender_mesh: _description_
    :type blender_mesh: Mesh
    :param list_point_data: _description_
    :type list_point_data: str
    :param time_point: _description_
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
