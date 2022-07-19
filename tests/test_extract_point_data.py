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


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_extract_point_data_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    # Get test data
    var_name = sample["extracted_value"]["name"]
    vertex_id = sample["extracted_value"]["vertex_id"]
    data = utils.get_point_data_telemac('2D').get(var_name).dumps()

    # Note: Fudaa count indices from 1 to xxx. Here we count indices from 0 to xxx.
    op = bpy.ops.tbb.telemac_extract_point_data
    state = op('EXEC_DEFAULT', mode='TEST', vertex_id=vertex_id - 1, max=10, start=0, end=10, test_data=data)
    assert state == {'FINISHED'}

    # Test keyframes
    assert len(obj.animation_data.action.fcurves) == 1
    fcurve = obj.animation_data.action.fcurves[0]
    assert fcurve.data_path == f'["{var_name}"]'
    assert fcurve.range()[0] == 0.0
    assert fcurve.range()[1] == 10.0

    # Test extracted values
    ground_truth = sample["extracted_value"]["values"]

    for value, id in zip(ground_truth, range(len(ground_truth))):
        # ------------------------------------------------------------ #
        # /!\ WARNING: next tests are based on the following frame /!\ #
        # ------------------------------------------------------------ #
        # Change frame to load time point 'id'
        bpy.context.scene.frame_set(id)

        assert id == bpy.context.scene.frame_current
        utils.compare_point_data_value(abs(obj[var_name] - value), var_name)


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_extract_point_data_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Get test data
    var_name = sample["extracted_value"]["name"]
    vertex_id = sample["extracted_value"]["vertex_id"]
    plane_id = sample["extracted_value"]["plane_id"]
    data = utils.get_point_data_telemac('3D').get(var_name).dumps()

    # Note: Fudaa count indices from 1 to xxx. Here we count indices from 0 to xxx.
    op = bpy.ops.tbb.telemac_extract_point_data
    state = op('EXEC_DEFAULT', mode='TEST', vertex_id=vertex_id - 1, max=10, start=0, end=10,
               test_data=data, plane_id=plane_id)
    assert state == {'FINISHED'}

    # Test keyframes
    assert len(obj.animation_data.action.fcurves) == 1
    fcurve = obj.animation_data.action.fcurves[0]
    assert fcurve.data_path == f'["{var_name}"]'
    assert fcurve.range()[0] == 0.0
    assert fcurve.range()[1] == 10.0

    # Test extracted values
    ground_truth = sample["extracted_value"]["values"]

    for value, id in zip(ground_truth, range(len(ground_truth))):
        # ------------------------------------------------------------ #
        # /!\ WARNING: next tests are based on the following frame /!\ #
        # ------------------------------------------------------------ #
        # Change frame to load time point 'id'
        bpy.context.scene.frame_set(id)

        assert id == bpy.context.scene.frame_current
        utils.compare_point_data_value(abs(obj[var_name] - value), var_name)
