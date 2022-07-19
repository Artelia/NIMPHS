# <pep8 compliant>
from bpy.types import Mesh

import logging
log = logging.getLogger(__name__)

import json
import numpy as np
from typing import Union
from copy import deepcopy
from tbb.operators.utils.others import remap_array
from tbb.properties.utils.interpolation import InterpInfo
from tbb.properties.utils.point_data import PointDataManager
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class VertexColorInformation():
    """Utility class which hold information on vertex colors to generate."""

    def __init__(self, nb_vertex_indices: int = 0) -> None:
        """
        Init method of the class.

        Args:
            nb_vertex_indices (int, optional): number of vertex indices. Defaults to 0.
        """

        self.names = []
        self.data = []
        self.nb_vertex_indices = nb_vertex_indices

    def groups(self) -> tuple[list[str], list[list[int]]]:
        """
        Generate vertex colors groups.

        Returns:
            tuple[list[str], list[list[int]]]: name of the group, indices of point data
        """

        if len(self.names) == 0:
            return [], []

        GRP_SIZE = 3
        size, grp_name, indices = 0, "", []
        grp_names, grp_indices = [], []

        for name, id in zip(self.names, range(len(self.names))):

            if size >= GRP_SIZE:
                grp_names.append(grp_name[:-2])
                grp_indices.append(deepcopy(indices))
                size, grp_name = 0, ""
                indices.clear()

            grp_name += f"{name}, "
            indices.append(id)
            size += 1

        # If last group is not full, fill it
        if GRP_SIZE - len(indices) > 0:
            for id in range(GRP_SIZE - len(indices)):
                grp_name += "None, "
                indices.append(-1)

        # Add last group
        grp_names.append(grp_name[:-2])
        grp_indices.append(deepcopy(indices))

        return grp_names, grp_indices

    def is_empty(self) -> bool:
        """
        Indicate whether 'names' array is empty.

        Returns:
            bool: state
        """

        return len(self.names) <= 0

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        return "{" + f"\n  names: {self.names},\n  data: {self.data},\n\
  nb_vertex_indices: {self.nb_vertex_indices},\n  empty: {self.is_empty()}" + "\n}"


class VertexColorUtils():
    """Utility functions for generating vertex colors for both modules."""

    @classmethod
    def generate(cls, bmesh: Mesh, data: VertexColorInformation) -> None:
        """
        Generate vertex colors for the given mesh.

        Args:
            bmesh (Mesh): mesh on which to add vertex colors
            data (VertexColorInformation):  point data information to generate vertex colors
        """

        # Data for alpha and empty channels
        ones = np.ones((data.nb_vertex_indices,))
        zeros = np.zeros((data.nb_vertex_indices,))

        grp_names, grp_indices = data.groups()

        for name, indices in zip(grp_names, grp_indices):
            vertex_colors = bmesh.vertex_colors.new(name=name, do_init=True)

            colors = []
            for id in indices:
                if id != -1:
                    colors.append(np.array(data.data[id]))
                else:
                    colors.append(zeros)

            # Add ones for alpha channel
            colors.append(ones)

            # Reshape data
            colors = np.array(colors).T

            colors = colors.flatten()
            vertex_colors.data.foreach_set("color", colors)


class TelemacVertexColorUtils(VertexColorUtils):
    """Utility functions for generating vertex colors for the TELEMAC module."""

    @classmethod
    def prepare(cls, bmesh: Mesh, point_data: Union[TBB_PointDataSettings, str], file_data: TBB_TelemacFileData,
                offset: int = 0) -> VertexColorInformation:
        """
        Prepare point data to generate vertex colors.

        Args:
            bmesh (Mesh): blender mesh
            point_data (Union[TBB_PointDataSettings, str]): point data settings
            file_data (TBB_TelemacFileData): file data
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.

        Returns:
            VertexColorInformation: point data information to generate vertex colors
        """

        # Prepare the mesh to loop over all its triangles
        if len(bmesh.loop_triangles) == 0:
            bmesh.calc_loop_triangles()

        # Get vertex indices
        vertex_ids = np.array([triangle.vertices for triangle in bmesh.loop_triangles]).flatten()

        # If point_data is string, then the request comes from the preview panel, so use 'LOCAL' method
        if isinstance(point_data, str):
            method = 'LOCAL'
            names = [] if json.loads(point_data)["name"] == 'None' else [json.loads(point_data)["name"]]
        else:
            method = point_data.remap_method
            names = PointDataManager(point_data.list).names

        output = VertexColorInformation(len(vertex_ids))

        for name in names:
            # Read data
            data = file_data.get_point_data(name)

            # Get right range of data in case of 3D simulation
            if file_data.is_3d():
                start_id = offset * file_data.nb_vertices
                end_id = offset * file_data.nb_vertices + file_data.nb_vertices
                data = data[start_id:end_id]

            # Get value range
            if method == 'LOCAL':
                # Update point data information
                file_data.update_var_range(name, scope=method)
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minL, var_range.maxL

            if method == 'GLOBAL':
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minG, var_range.maxG

            # Append point data to output list
            output.names.append(name)
            output.data.append(remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max))

        return output

    @classmethod
    def prepare_LI(cls, bmesh: Mesh, point_data: TBB_PointDataSettings, file_data: TBB_TelemacFileData,
                   time_info: InterpInfo, offset: int = 0) -> VertexColorInformation:
        """
        Prepare point data for linear interpolation of TELEMAC sequences.

        Args:
            bmesh (Mesh): blender mesh
            point_data (TBB_PointDataSettings): point data settings
            file_data (TBB_TelemacFileData): file data
            time_info (InterpInfo): time information
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.

        Returns:
            VertexColorInformation: point data information to generate vertex colors
        """

        # Get data from left time point
        file_data.update_data(time_info.left)
        left = cls.prepare(bmesh, point_data, file_data, offset=offset)

        if not time_info.exists:
            # Get data from right time point
            file_data.update_data(time_info.right)
            right = cls.prepare(bmesh, point_data, file_data, offset=offset)

            percentage = np.abs(time_info.frame - time_info.left_frame) / (time_info.time_steps + 1)

            # Linearly interpolate
            interpolated = left
            for id in range(len(interpolated["names"])):
                interpolated.data[id] = left.data[id] + (right.data[id] - left.data[id]) * percentage

            return interpolated

        else:
            # If it is an existing time point, no need to interpolate
            return left


class OpenfoamVertexColorUtils(VertexColorUtils):
    """Utility functions for generating vertex colors for the OpenFOAM module."""

    @classmethod
    def prepare(cls, bmesh: Mesh, point_data: Union[TBB_PointDataSettings, str],
                file_data: TBB_OpenfoamFileData) -> VertexColorInformation:
        """
        Prepare point data to generate vertex colors.

        Args:
            bmesh (Mesh): blender mesh
            point_data (Union[TBB_PointDataSettings, str]): point data settings
            file_data (TBB_OpenfoamFileData): file data

        Returns:
            VertexColorInformation: vertex colors groups, color data, number of vertices
        """

        # Prepare the mesh to loop over all its triangles
        if len(bmesh.loop_triangles) == 0:
            bmesh.calc_loop_triangles()

        # Get vertex indices
        vertex_ids = np.array([triangle.vertices for triangle in bmesh.loop_triangles]).flatten()

        # If point_data is string, then the request comes from the preview panel, so use 'LOCAL' method
        if isinstance(point_data, str):
            method = 'LOCAL'
            names = [] if json.loads(point_data)["name"] == 'None' else [json.loads(point_data)["name"]]
        else:
            method = point_data.remap_method
            names = PointDataManager(point_data.list).names

        output = VertexColorInformation(len(vertex_ids))

        for name in names:
            # Read data
            data = file_data.get_point_data(name)[vertex_ids]

            # Get value range
            if method == 'LOCAL':
                # Update point data information
                file_data.update_var_range(name, scope=method)
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minL, var_range.maxL

            if method == 'GLOBAL':
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minG, var_range.maxG

            # Append point data to output list
            output.names.append(name)
            output.data.append(remap_array(np.array(data), in_min=min, in_max=max))

        return output
