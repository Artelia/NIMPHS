# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import warnings

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_generate_volume_sequence_openfoam():
    pytest.skip(reason="Not implemented yet")


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #

def test_generate_volume_sequence_telemac_3d_default():
    # Import TELEMAC 3D sample object
    op = bpy.ops.nimphs.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Set test data:
    data = json.dumps({
        "point_data": sample["point_data"]["names"][0],
        "start": 0,
        "end": (sample["nb_time_points"] - 1) // 2,
        "max": sample["nb_time_points"] - 1,
        "computing_mode": "DEFAULT",
        "nb_threads": 0,
        "output_path": os.path.abspath("./cache"),
        "file_name": "test_volume_telemac_3d_default",
        "dim_x": 50,
        "dim_y": 50,
        "dim_z": 50,
        "time_interpolation": 1,
        "space_interpolation": 3,
    })

    # TODO: when pyopenvdb installation is fixed, change 'CANCELLED' to 'FINISH' to run the test
    op = bpy.ops.nimphs.telemac_generate_volume_sequence
    assert op('EXEC_DEFAULT', mode='TEST', test_data=data) == {'CANCELLED'}
    warnings.warn(UserWarning(f"Test is not fully implemented yet"))


def test_generate_volume_sequence_telemac_3d_multiprocessing():
    # Select preview object
    utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Set test data:
    data = json.dumps({
        "point_data": sample["point_data"]["names"][0],
        "start": 0,
        "end": (sample["nb_time_points"] - 1) // 2,
        "max": sample["nb_time_points"] - 1,
        "computing_mode": "MULTIPROCESSING",
        "nb_threads": len(os.sched_getaffinity(0)),  # Number of available threads
        "output_path": os.path.abspath("./cache"),
        "file_name": "test_volume_telemac_3d_multiprocessing",
        "dim_x": 50,
        "dim_y": 50,
        "dim_z": 50,
        "time_interpolation": 1,
        "space_interpolation": 3,
    })

    # TODO: when pyopenvdb installation is fixed, change 'CANCELLED' to 'FINISH' to run the test
    op = bpy.ops.nimphs.telemac_generate_volume_sequence
    assert op('EXEC_DEFAULT', mode='TEST', test_data=data) == {'CANCELLED'}
    warnings.warn(UserWarning(f"Test is not fully implemented yet"))


@pytest.mark.usefixtures("clean_all_objects")
def test_generate_volume_sequence_telemac_3d_cuda():
    # Select preview object
    utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Set test data:
    data = json.dumps({
        "point_data": sample["point_data"]["names"][0],
        "start": 0,
        "end": (sample["nb_time_points"] - 1) // 2,
        "max": sample["nb_time_points"] - 1,
        "computing_mode": "CUDA",
        "nb_threads": 0,  # Number of available threads
        "output_path": os.path.abspath("./cache"),
        "file_name": "test_volume_telemac_3d_cuda",
        "dim_x": 50,
        "dim_y": 50,
        "dim_z": 50,
        "time_interpolation": 1,
        "space_interpolation": 3,
    })

    # TODO: when pyopenvdb installation is fixed, change 'CANCELLED' to 'FINISH' to run the test
    op = bpy.ops.nimphs.telemac_generate_volume_sequence
    assert op('EXEC_DEFAULT', mode='TEST', test_data=data) == {'CANCELLED'}
    warnings.warn(UserWarning(f"Test is not fully implemented yet"))
