# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest

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


@pytest.mark.usefixtures("clean_all_objects")
def test_generate_volume_sequence_telemac_3d_multiprocessing():
    # Import TELEMAC 3D sample object
    op = bpy.ops.nimphs.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Set test data:
    data = json.dumps({
        "point_data": sample["point_data"]["names"][0],
        "start": 0,
        "end": sample["nb_times_points"] - 1,
        "max": sample["nb_time_points"] - 1,
        "computing_mode": "MULTIPROCESSING",
        "nb_threads": 4,
        "output_path": os.path.abspath("."),
        "file_name": "test_volume_telemac_3d",
        "dim_x": 100,
        "dim_y": 100,
        "dim_z": 40,
        "time_interpolation": 2,
        "space_interpolation": 5,
    })

    op = bpy.ops.nimphs.telemac_generate_volume_sequence
    assert op('EXEC_DEFAULT', mode='TEST', test_data=data) == {'FINISHED'}
