# <pep8 compliant>
import bpy
from bpy.types import Object

import logging
log = logging.getLogger(__name__)

import numpy as np
from typing import Union
from tbb.operators.utils.mesh import TelemacMeshUtils
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings


class ObjectUtils():

    @classmethod
    def generate(cls, vertices: np.ndarray, faces: np.ndarray, name: str, new: bool = False) -> Object:
        """
        Generate an object and its mesh using the given vertices and faces.

        If it already exists, clear object data and use the given data as new data.

        Args:
            vertices (np.ndarray): vertices, must have the following shape: (n, 3)
            faces (np.ndarray): faces, must have the following shape: (n, 3)
            name (str): name of the object
            new (bool): force to generate a new object

        Returns:
            Object: generated object
        """

        obj = bpy.data.objects.get(name) if not new else None
        if obj is None:
            bmesh = bpy.data.meshes.get(name + "_mesh") if not new else None
            if bmesh is None:
                bmesh = bpy.data.meshes.new(name + "_mesh")

            obj = bpy.data.objects.new(name, bmesh)
        else:
            bmesh = obj.data

        obj.shape_key_clear()
        bmesh.clear_geometry()
        bmesh.from_pydata(vertices, [], faces)

        return obj


class TelemacObjectUtils():

    @classmethod
    def base(file_data: TBB_TelemacFileData, name: str,
             point_data: Union[TBB_PointDataSettings, str] = "") -> list[Object]:
        """
        Generate objects using settings defined by the user. This function generates objects and vertex colors.

        If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth").
        If the file is a 3D simulation, this will generate one object per plane.

        Args:
            file_data (TBB_TelemacFileData): file data
            name (str): name to give to the objects
            point_data (Union[TBB_PointDataSettings, str], optional): point data settings. Defaults to "".

        Returns:
            list[Object]: generated objects
        """

        # Check if we need to import point data
        if isinstance(point_data, str):
            import_point_data = point_data != ""
        else:
            import_point_data = point_data.import_data

        objects = []
        if not file_data.is_3d():

            for type in ['BOTTOM', 'WATER_DEPTH']:

                vertices = TelemacMeshUtils.vertices(file_data, type=type)
                obj = ObjectUtils.generate(vertices, file_data.faces, name=f"{name}_{type.lower()}")
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = type

                if import_point_data:
                    res = prepare_telemac_point_data(obj.data, point_data, file_data)
                    generate_vertex_colors(obj.data, *res)

                objects.append(obj)
        else:
            for plane_id in range(file_data.nb_planes - 1, -1, -1):
                vertices = TelemacMeshUtils.vertices(file_data, offset=plane_id)
                obj = ObjectUtils.generate(vertices, file_data.faces, name=f"{name}_plane_{plane_id}")
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = str(plane_id)

                if import_point_data:
                    res = prepare_telemac_point_data(obj.data, point_data, file_data, offset=plane_id)
                    generate_vertex_colors(obj.data, *res)

                objects.append(obj)

        return objects
