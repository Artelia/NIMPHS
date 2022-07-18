# <pep8 compliant>
from bpy.types import Object

import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Union
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.utils.interpolation import InterpInfo


class TelemacMeshUtils():
    """Utility functions for generating meshes for the TELEMAC module."""

    @classmethod
    def vertices(cls, file_data: TBB_TelemacFileData, offset: int = 0, type: str = 'BOTTOM') -> Union[np.ndarray, None]:
        """
        Generate vertices of the mesh.

        If the selected file is a 2D simulation, you can precise which part of the mesh\
        you want ('BOTTOM' or 'WATER_DEPTH').
        If the file is a 3D simulation, you can precise an offset for data\
        reading (this offsets is somehow the id of the plane to generate).

        Args:
            file_data (TBB_TelemacFileData): file data
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.
            type (str, optional): name of the variable to use as z-values. Defaults to 'BOTTOM'.

        Returns:
            Union[np.ndarray, None]: vertices
        """

        if not file_data.is_3d() and type not in ['BOTTOM', 'WATER_DEPTH']:
            log.error("Undefined type, please use one in ['BOTTOM', 'WATER_DEPTH']")
            return None

        if file_data.is_3d():
            # Get data for z-values
            data, name = file_data.get_point_data_from_list(["ELEVATION Z", "COTE Z"])

            # Ids from where to read data in the z-values array
            start_id, end_id = offset * file_data.nb_vertices, offset * file_data.nb_vertices + file_data.nb_vertices
            vertices = np.hstack((file_data.vertices, data[start_id:end_id]))

        else:
            if type == 'BOTTOM':
                # Get data for z-values
                data, name = file_data.get_point_data_from_list(["BOTTOM", "FOND"])
                vertices = np.hstack((file_data.vertices, data))

            if type == 'WATER_DEPTH':
                # Get data for z-values
                data, name = file_data.get_point_data_from_list(["WATER DEPTH", "HAUTEUR D'EAU",
                                                                 "FREE SURFACE", "SURFACE LIBRE"])

                # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                if name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                    # Get data for z-values
                    bottom = file_data.get_point_data_from_list(["BOTTOM", "FOND"])
                    data += bottom

                vertices = np.hstack((file_data.vertices, data))

        return vertices

    @classmethod
    def vertices_LI(cls, obj: Object, file_data: TBB_TelemacFileData, time_info: InterpInfo,
                    offset: int = 0) -> np.ndarray:
        """
        Generate linearly interpolated vertices of the mesh.

        Args:
            obj (Object): object
            file_data (TBB_TelemacFileData): file data
            time_info (InterpInfo): time information
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.

        Returns:
            np.ndarray: vertices
        """

        # Get data from left time point
        file_data.update_data(time_info.left)
        left = cls.vertices(file_data, offset=offset, type=obj.tbb.settings.telemac.z_name)

        if not time_info.exists:
            # Get data from right time point
            file_data.update_data(time_info.right)
            right = cls.vertices(file_data, offset=offset, type=obj.tbb.settings.telemac.z_name)

            percentage = np.abs(time_info.frame - time_info.left) / (time_info.time_steps + 1)

            return (left.T + (right.T - left.T) * percentage).T

        else:
            # If it is an existing time point, no need to interpolate
            return left
