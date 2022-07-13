# <pep8 compliant>
import os
import bpy
import json
import numpy as np
from bpy.types import Object, MeshLoopColorLayer

# Point data value threshold for tests
PDV_THRESHOLD = 0.01

# Object names
PREVIEW_OBJ_NAME = "Preview"
MESH_SEQUENCE_OBJ_NAME = "Mesh"
STREAMING_SEQUENCE_OBJ_NAME = "Streaming"

# Files
FILE_PATH_OPENFOAM = os.path.abspath("./data/openfoam_sample_a/foam.foam")
FILE_PATH_TELEMAC_2D = os.path.abspath("./data/telemac_2d_sample/telemac_2d.slf")
FILE_PATH_TELEMAC_3D = os.path.abspath("./data/telemac_3d_sample/telemac_3d.slf")

# Sample information
SAMPLE_OPENFOAM = os.path.abspath("./data/openfoam_sample_a/SAMPLE.json")
SAMPLE_TELEMAC_2D = os.path.abspath("./data/telemac_2d_sample/SAMPLE.json")
SAMPLE_TELEMAC_3D = os.path.abspath("./data/telemac_3d_sample/SAMPLE.json")

def get_sample_data(path: str):
    file = open(path, "r")
    data = json.load(file)
    file.close()
    return data


def get_preview_object():
    obj = bpy.data.objects.get(PREVIEW_OBJ_NAME, None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj

def clean_objects():
    """Clean all mesh objects."""

    meshes = set()
    for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
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
    Compute mean value of the selcted color channel.

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
