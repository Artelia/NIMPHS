# <pep8 compliant>
import os
import sys
import bpy
import pytest

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_compute_ranges_point_data_values_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', mode='TEST', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=utils.get_point_data_openfoam(True).dumps()) == {'FINISHED'}


@pytest.mark.usefixtures("clean_all_objects")
def test_computed_min_max_values_openfoam():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["values"]["skip_zero_true"]

    # Get file data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test computed values
    point_data = utils.get_point_data_openfoam(True)
    for name in point_data.names:
        data = file_data.vars.get(name, prop='RANGE')

        ground_truth = {"max": vars[name]["max"], "min": vars[name]["min"]}
        assert data.minG == ground_truth["min"]
        assert data.maxG == ground_truth["max"]


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_compute_ranges_point_data_values_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=utils.get_point_data_telemac('2D').dumps()) == {'FINISHED'}


@pytest.mark.usefixtures("clean_all_objects")
def test_computed_min_max_values_telemac_2d():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    vars = sample["values"]

    # Get file data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test computed values
    point_data = utils.get_point_data_telemac('2D')
    for name in point_data.names:
        data = file_data.vars.get(name, prop='RANGE')

        ground_truth = {"max": vars[name]["max"], "min": vars[name]["min"]}
        assert data.minG == ground_truth["min"]
        assert data.maxG == ground_truth["max"]


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_compute_ranges_point_data_values_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=utils.get_point_data_telemac('3D').dumps()) == {'FINISHED'}


@pytest.mark.usefixtures("clean_all_objects")
def test_computed_min_max_values_telemac_3d():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)
    vars = sample["values"]

    # Get file data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test computed values
    point_data = utils.get_point_data_telemac('3D')
    for name in point_data.names:
        data = file_data.vars.get(name, prop='RANGE')

        ground_truth = {"max": vars[name]["max"], "min": vars[name]["min"]}
        assert data.minG == ground_truth["min"]
        assert data.maxG == ground_truth["max"]
