# <pep8 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.types import Mesh, Object, Context, Scene

import logging
log = logging.getLogger(__name__)

import time
import numpy as np
from typing import Union
from copy import deepcopy

from tbb.properties.utils import VariablesInformation
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.properties.utils import InterpInfoMeshSequence, InterpInfoStreamingSequence, InterpInfo
from tbb.operators.telemac.Scene.telemac_create_mesh_sequence import TBB_OT_TelemacCreateMeshSequence
from tbb.operators.utils import (
    generate_object_from_data,
    remap_array,
    generate_vertex_colors_groups,
    generate_vertex_colors
)


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


@persistent
def update_telemac_streaming_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'streaming sequences' of the scene.

    Args:
        scene (Scene): scene
    """

    # Check if a create sequence operator is running
    if scene.tbb.m_op_running:
        return

    for obj in scene.objects:
        # Check if current object is a streaming sequence
        if not obj.tbb.is_streaming_sequence:
            continue

        sequence = obj.tbb.settings.telemac.s_sequence
        interpolate = obj.tbb.settings.telemac.interpolate

        if sequence.update:
            # Get file data
            try:
                file_data = scene.tbb.file_data[obj.tbb.uid]
            except KeyError:
                # Disable update
                sequence.update = False
                log.error(f"No file data available for {obj.name}. Disabling update.")
                return

            # Compute limit (last time point to compute, takes interpolation into account)
            limit = sequence.start + sequence.length
            if interpolate.type != 'NONE':
                limit += (sequence.length - 1) * interpolate.time_steps

            if scene.frame_current >= sequence.start and scene.frame_current < limit:
                start = time.time()

                for child, id in zip(obj.children, range(len(obj.children))):
                    offset = id if file_data.is_3d() else 0
                    update_telemac_streaming_sequence(obj, child, file_data, scene.frame_current, offset)

                log.info(obj.name + ", " + "{:.4f}".format(time.time() - start) + "s")


def update_telemac_streaming_sequence(obj: Object, child: Object, file_data: TBB_TelemacFileData,
                                      frame: int, offset: int) -> None:
    """
    Update the mesh of the given 'child' object from a TELEMAC 'streaming sequence' object.

    Args:
        obj (Object): sequence object
        child (Object): child object of the sequence
        file_data (TBB_TelemacFileData): file data
        frame (int): frame
        offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.
    """

    # Get settings
    interpolate = obj.tbb.settings.telemac.interpolate
    sequence = obj.tbb.settings.telemac.s_sequence
    point_data = obj.tbb.settings.point_data

    # Update mesh
    if interpolate.type == 'LINEAR':
        time_info = InterpInfoStreamingSequence(frame, sequence.start, interpolate.time_steps)
        vertices = generate_mesh_data_linear_interp(child, file_data, time_info, offset)

    else:
        time_point = frame - sequence.start
        vertices = generate_mesh_data(file_data, offset=offset, type=child.tbb.settings.telemac.z_name)

    # Generate object
    child = generate_object_from_data(vertices, file_data.faces, child.name)

    # Apply smooth shading
    if sequence.shade_smooth:
        child.data.polygons.foreach_set("use_smooth", [True] * len(child.data.polygons))

    # Update point data
    if point_data.import_data:
        # Remove old vertex colors
        while child.data.vertex_colors:
            child.data.vertex_colors.remove(child.data.vertex_colors[0])

        # Update vertex colors data
        if interpolate.type == 'LINEAR':
            res = prepare_telemac_point_data_linear_interp(child.data, point_data, file_data, time_info, offset=offset)
        elif interpolate.type == 'NONE':
            file_data.update_data(time_point)
            res = prepare_telemac_point_data(child.data, point_data, file_data, offset=offset)

        generate_vertex_colors(child.data, *res)

        # Update information of selected point data
        new_information = VariablesInformation()
        selected = VariablesInformation(point_data.list)
        for var in selected.names:
            new_information.append(data=file_data.vars.get(var))
        point_data.list = new_information.dumps()


@persistent
def update_telemac_mesh_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'mesh sequence' objects.

    Args:
        scene (Scene): scene
    """

    # Check if a create sequence operator is running
    if scene.tbb.m_op_running:
        return

    for obj in scene.objects:
        # Check if current object is a mesh sequence
        if not obj.tbb.is_mesh_sequence:
            continue

        point_data = obj.tbb.settings.point_data

        # Check if there are point data to import as vertex colors
        if point_data.import_data and VariablesInformation(point_data.list).length() > 0:
            # sequence = obj.tbb.settings.telemac.m_sequence

            # Get file data
            try:
                file_data = scene.tbb.file_data[obj.tbb.uid]
            except KeyError:
                # Disable update
                point_data.import_data = False
                log.error(f"No file data available for {obj.name}. Disabling update.")
                return

            # Update children of the sequence object
            cumulated_time = 0.0

            for child, id in zip(obj.children, range(len(obj.children))):
                start = time.time()

                # Get interpolation time information
                time_info = InterpInfoMeshSequence(child, scene.frame_current)
                if time_info.has_data:
                    offset = id if file_data.is_3d() else 0
                    update_telemac_mesh_sequence(child.data, file_data, offset, point_data, time_info)

                cumulated_time += time.time() - start

            if cumulated_time > 0.0:
                log.info(obj.name + ", " + "{:.4f}".format(cumulated_time) + "s")


def update_telemac_mesh_sequence(bmesh: Mesh, file_data: TBB_TelemacFileData, offset: int,
                                 point_data: TBB_PointDataSettings, time_info: InterpInfo) -> None:
    """
    Update the given TELEMAC 'mesh sequence' child object.

    Args:
        bmesh (Mesh): blender mesh
        file_data (TBB_TelemacFileData): file data
        offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.
        point_data (TBB_PointDataSettings): point data
        time_info (InterpInfo): time information
    """

    # Remove existing vertex colors
    while bmesh.vertex_colors:
        bmesh.vertex_colors.remove(bmesh.vertex_colors[0])

    # Update point data
    res = prepare_telemac_point_data_linear_interp(bmesh, point_data, file_data, time_info, offset=offset)
    generate_vertex_colors(bmesh, *res)

    # Update information of selected point data
    new_information = VariablesInformation()
    selected = VariablesInformation(point_data.list)
    for var in selected.names:
        new_information.append(data=file_data.vars.get(var))
    point_data.list = new_information.dumps()
