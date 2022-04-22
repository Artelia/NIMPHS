# <pep8 compliant>
from bpy.types import Context, Mesh

import numpy as np

from ..utils import update_dynamic_props
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
    name = ""
    for var_id, num in zip(var_id_groups, range(3)):
        if var_id != -1:
            name += tmp_data.variables_info["names"][var_id]
        else:
            name += "NONE"

        name += (", " if num != 2 else "")

    return name


def generate_vertex_colors(tmp_data: TBB_TelemacTemporaryData, blender_mesh: Mesh,
                           list_point_data: str, time_point: int):
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
                colors.append(np.array(data[var_id])[vertex_ids])
            else:
                colors.append(zeros)

        # Add ones for alpha channel
        colors.append(ones)

        # Reshape data
        colors = np.array(colors).T

        print(colors)
        colors = colors.flatten()
        print(len(vertex_colors.data), len(vertex_ids), len(colors), len(tmp_data.vertices))
        # vertex_colors.data.foreach_set("color", data)
