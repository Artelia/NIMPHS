# <pep8 compliant>
from bpy.types import Object, Mesh

import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Union
from tbb.operators.utils.others import remap_array
from tbb.properties.utils.interpolation import InterpInfo
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.utils.point_data_manager import PointDataManager
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class VertexColorsInformation():

    def __init__(self, nb_vertex_indices: int = 0) -> None:
        self.names = []
        self.data = []
        self.nb_vertex_indices = nb_vertex_indices

    def groups(self) -> tuple[list[str], list[list[int]]]:
        """
        Generate vertex colors groups.

        Returns:
            tuple[list[str], list[list[int]]]: name of the group, indices of point data
        """

        GRP_SIZE = 3
        size, grp_name, indices = 0, "", []
        grp_names, grp_indices = [], []

        for name, id in zip(self.names, range(len(self.names))):

            if size >= GRP_SIZE:
                grp_names.append(grp_name[:-2])
                grp_indices.append(indices)
                size, grp_name = 0, ""
                indices.clear()

            grp_name += f"{name}, "
            indices.append(id)
            size += 1

        # If last group is not full, fill it
        for id in range(GRP_SIZE - len(grp_names)):
            grp_name += f"{name}, "
            indices.append(-1)

        # Add last group
        grp_names.append(grp_name[:-2])
        grp_indices.append(indices)

        return grp_names, grp_indices


class PointDataUtils():

    @classmethod
    def vertex_colors(cls, bmesh: Mesh, data: VertexColorsInformation) -> None:
        """
        Generate vertex colors for the given mesh.

        Args:
            bmesh (Mesh): mesh on which to add vertex colors
            VertexColorsInformation (np.ndarray):  point data information to generate vertex colors
        """

        # Data for alpha and empty channels
        ones = np.ones((data.nb_vertex_indices,))
        zeros = np.zeros((data.nb_vertex_indices,))

        for name, indices in data.groups():
            vertex_colors = bmesh.vertex_colors.new(name=name, do_init=True)

            colors = []
            for id in indices:
                if id != -1:
                    colors.append(np.array(data[id]))
                else:
                    colors.append(zeros)

            # Add ones for alpha channel
            colors.append(ones)

            # Reshape data
            colors = np.array(colors).T

            colors = colors.flatten()
            vertex_colors.data.foreach_set("color", colors)

    @classmethod
    def telemac(cls, bmesh: Mesh, point_data: Union[TBB_PointDataSettings, str], file_data: TBB_TelemacFileData,
                offset: int = 0) -> VertexColorsInformation:
        """
        Prepare point data for the 'generate vertex colors' process.

        Args:
            bmesh (Mesh): blender mesh
            point_data (Union[TBB_PointDataSettings, str]): point data settings
            file_data (TBB_TelemacFileData): file data
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.

        Returns:
            VertexColorsInformation: point data information to generate vertex colors
        """

        # Prepare the mesh to loop over all its triangles
        if len(bmesh.loop_triangles) == 0:
            bmesh.calc_loop_triangles()

        # Get vertex indices
        vertex_ids = np.array([triangle.vertices for triangle in bmesh.loop_triangles]).flatten()

        # If point_data is string, then the request comes from the preview panel, so use 'LOCAL' method
        method = 'LOCAL' if isinstance(point_data, str) else point_data.remap_method

        output = VertexColorsInformation(len(vertex_ids))

        for name in file_data.vars.names:
            # Read data
            data = file_data.get_point_data(name)

            # Get right range of data in case of 3D simulation
            if file_data.is_3d():
                start_id, end_id = offset * file_data.nb_vertices, offset * file_data.nb_vertices + file_data.nb_vertices
                data = data[start_id:end_id]

            # Get value range
            if method == 'LOCAL':
                # Update point data information
                file_data.update_var_range(name, scope=method)
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minL, var_range.maxL

            elif method == 'GLOBAL':
                var_range = file_data.vars.get(name, prop='RANGE')
                min, max = var_range.minG, var_range.maxG

            # Append point data to output list
            output.names.append(name)
            output.data.append(remap_array(np.array(data)[vertex_ids], in_min=min, in_max=max))

        return output

    @classmethod
    def telemac_LI(cls, bmesh: Mesh, point_data: TBB_PointDataSettings, file_data: TBB_TelemacFileData,
                   time_info: InterpInfo, offset: int = 0) -> VertexColorsInformation:
        """
        Prepare point data for linear interpolation of TELEMAC sequences.

        Args:
            bmesh (Mesh): blender mesh
            point_data (TBB_PointDataSettings): point data settings
            file_data (TBB_TelemacFileData): file data
            time_info (InterpInfo): time information
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.

        Returns:
            VertexColorsInformation: point data information to generate vertex colors
        """

        # Get data from left time point
        file_data.update_data(time_info.left)
        left = cls.telemac(bmesh, point_data, file_data, offset=offset)

        if not time_info.exists:
            # Get data from right time point
            file_data.update_data(time_info.right)
            right = cls.telemac(bmesh, point_data, file_data, offset=offset)

            percentage = np.abs(time_info.frame - time_info.left_frame) / (time_info.time_steps + 1)

            # Linearly interpolate
            interpolated = left
            for id in range(len(interpolated["names"])):
                interpolated.data[id] = left.data[id] + (right.data[id] - left.data[id]) * percentage

            return interpolated

        else:
            # If it is an existing time point, no need to interpolate
            return left
