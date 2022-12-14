# <pep8 compliant>
import bpy
from bpy.types import Object, MeshLoopColorLayer

import os
import json
import pytest
import warnings
import numpy as np

from nimphs.properties.utils.point_data import PointDataManager

# Point data value threshold for tests
PDV_THRESHOLD = 0.01

# Object names
PRW_OBJ_NAME = "Preview"
MESH_SEQUENCE_OBJ_NAME = "Mesh_sequence"
STREAMING_SEQUENCE_OBJ_NAME = "Streaming_sequence"

# Files
FILE_PATH_OPENFOAM = os.path.abspath("./data/openfoam/sample/foam.foam")
FILE_PATH_TELEMAC_2D = os.path.abspath("./data/telemac_2d/telemac_2d.slf")
FILE_PATH_TELEMAC_3D = os.path.abspath("./data/telemac_3d/telemac_3d.slf")

# Sample information
SAMPLE_OPENFOAM = os.path.abspath("./data/openfoam/SAMPLE.json")
SAMPLE_TELEMAC_2D = os.path.abspath("./data/telemac_2d/SAMPLE.json")
SAMPLE_TELEMAC_3D = os.path.abspath("./data/telemac_3d/SAMPLE.json")


def compare_point_data_value(subtraction: float, name: str):
    """
    Compare computed point data value VS ground truth.

    Args:
        subtraction (float): computed value VS ground truth
        name (str): name of the variable
    """

    if subtraction < 0.1 and subtraction > 0.01:
        warnings.warn(UserWarning(f"{name}, difference is high ({subtraction})."))
    else:
        assert subtraction < PDV_THRESHOLD


def get_sample_data(path: str):
    """
    Get sample data from the file at the given location.

    Args:
        path (str): path to json file
    """

    file = open(path, "r")
    data = json.load(file)
    file.close()
    return data


def get_point_data_openfoam(skip_zero_time: bool):
    """
    Get point data information for OpenFOAM sample.

    Args:
        skip_zero_time (bool): skip the '/0' time directory
    """

    sample = get_sample_data(SAMPLE_OPENFOAM)
    if skip_zero_time:
        info = sample["point_data"]["skip_zero_true"]
    else:
        info = sample["point_data"]["skip_zero_false"]

    point_data = PointDataManager()
    for name, unit in zip(info["names"], info["units"]):
        point_data.append(name=name, unit=unit)

    return point_data


def get_point_data_telemac(dim: str):
    """
    Get point data information for TELEMAC sample.

    Args:
        dim (str): enum in ['2D', '3D']
    """

    if dim == '2D':
        sample = get_sample_data(SAMPLE_TELEMAC_2D)
    if dim == '3D':
        sample = get_sample_data(SAMPLE_TELEMAC_3D)

    info = sample["point_data"]
    point_data = PointDataManager()
    for name, unit in zip(info["names"], info["units"]):
        point_data.append(name=name, unit=unit)

    return point_data


def get_preview_object():
    """Get preview object. If it does not exist, return None."""

    obj = bpy.data.objects.get(PRW_OBJ_NAME, None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj


@pytest.fixture
def clean_all_objects():
    """Clean all mesh objects."""

    yield

    # This code will be executed at the end of the test
    meshes = set()
    for obj in [o for o in bpy.data.objects if o.type in ['MESH', 'EMPTY']]:
        if obj.type == 'MESH':
            # Store the internal mesh
            meshes.add(obj.data)

        # Delete the object
        bpy.data.objects.remove(obj)

    # Look at meshes that are now orphean
    for mesh in [m for m in meshes if m.users == 0]:
        # Delete the mesh
        bpy.data.meshes.remove(mesh)


def compute_mean_value(colors: MeshLoopColorLayer, obj: Object, channel: int):
    """
    Compute mean value of the selected color channel.

    Args:
        colors (MeshLoopColorLayer): vertex color data
        obj (Object): object
        channel (int): selected color channel

    Returns:
        float: mean value
    """

    data = [0] * len(obj.data.loops) * 4
    colors.data.foreach_get("color", data)
    extracted = [data[i] for i in range(channel, len(data), 4)]
    return np.sum(extracted) / len(obj.data.loops)


def get_frame_change_pre_app_handler(name: str):
    """
    Get an app handler by string.

    Args:
        name (str): name of the app handler
    """

    for handler in bpy.app.handlers.frame_change_pre:
        if handler.__name__ == name:
            return handler

    return None


def get_frame_change_post_app_handler(name: str):
    """
    Get an app handler by string.

    Args:
        name (str): name of the app handler
    """

    for handler in bpy.app.handlers.frame_change_post:
        if handler.__name__ == name:
            return handler

    return None
