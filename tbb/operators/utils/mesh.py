# <pep8 compliant>
from copy import deepcopy
from bpy.types import Object

import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Union
from pyvista import PolyData, UnstructuredGrid
from tbb.properties.utils.interpolation import InterpInfo
from tbb.properties.utils.point_data import PointDataInformation
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.openfoam.clip import TBB_OpenfoamClipProperty
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData


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
                    bottom, name = file_data.get_point_data_from_list(["BOTTOM", "FOND"])
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

            percentage = np.abs(time_info.frame - time_info.left_frame) / (time_info.time_steps + 1)

            return (left.T + (right.T - left.T) * percentage).T

        else:
            # If it is an existing time point, no need to interpolate
            return left


class OpenfoamMeshUtils():
    """Utility functions for generating meshes for the OpenFOAM module."""

    @classmethod
    def vertices(cls, file_data: TBB_OpenfoamFileData,
                 clip: TBB_OpenfoamClipProperty = None) -> tuple[Union[np.ndarray, None], Union[PolyData, np.ndarray]]:
        """
        Generate vertices and extracted surface of the given OpenFOAM file.

        Args:
            file_data (TBB_OpenfoamFileData): file data
            clip (TBB_OpenfoamClipProperty, optional): clip settings. Defaults to None.

        Returns:
            tuple[Union[np.ndarray, None], Union[PolyData, np.ndarray]]: vertices, extracted surface
        """

        # Get raw mesh
        mesh = deepcopy(file_data.raw_mesh)
        if mesh is None:
            return None, None

        # Apply clip
        if clip is not None:
            surface = cls.clip(mesh, clip)
        else:
            surface = mesh.extract_surface(nonlinear_subdivision=0)

        # Triangulate
        if file_data.triangulate:
            surface.triangulate(inplace=True)
            surface.compute_normals(inplace=True, consistent_normals=False, split_vertices=True)

        return np.array(surface.points), surface

    @classmethod
    def faces(cls, surface: PolyData) -> Union[np.ndarray, None]:
        """
        Get faces array of an extracted surface.

        Args:
            surface (PolyData): extracted surface

        Returns:
            np.ndarray: faces array
        """

        if surface is None:
            return None

        if surface.is_all_triangles:
            faces = np.array(surface.faces).reshape(-1, 4)[:, 1:4]

        else:
            faces_indices = np.array(surface.faces)
            padding, padding_id = 0, 0
            faces = []

            for id in range(surface.n_faces):

                if padding_id >= faces_indices.size:
                    break

                padding = faces_indices[padding_id]
                faces.append(faces_indices[padding_id + 1: padding_id + 1 + padding])
                padding_id = padding_id + (padding + 1)

        return faces

    @classmethod
    def clip(cls, mesh: UnstructuredGrid, clip: TBB_OpenfoamClipProperty) -> Union[PolyData, None]:
        """
        Generate clipped surface.

        Args:
            mesh (UnstructuredGrid): mesh
            clip (TBB_OpenfoamClipProperty): clip settings

        Returns:
            Union[PolyData, None]: PolyData
        """

        # Apply clip
        if clip.type == 'SCALAR':
            info = PointDataInformation(json_string=clip.scalar.name)

            # Make sure there is a scalar selected
            if info.name != "None":

                channel = info.name.split('.')[-1]
                name = info.name[-2] if channel.isnumeric() else info.name

                mesh.set_active_scalars(name=name, preference="point")

                # Safely get the value (avoid using a value which is not in the range)
                if clip.scalar.value > info.range.maxL:
                    value = info.range.maxL
                elif clip.scalar.value < info.range.minL:
                    value = info.range.minL
                else:
                    value = clip.scalar.value

                mesh.clip_scalar(inplace=True, scalars=name, invert=clip.scalar.invert, value=value)
                surface = mesh.extract_surface(nonlinear_subdivision=0)
            else:
                log.warning("Can't apply clip. No scalar selected.")
                surface = mesh.extract_surface(nonlinear_subdivision=0)

        else:
            surface = mesh.extract_surface(nonlinear_subdivision=0)

        return surface
