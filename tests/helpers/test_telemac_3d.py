# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import numpy as np

sys.path.append(os.path.abspath("."))  # Make helpers module available in this file
from helpers import utils

FILE_PATH = os.path.abspath("./data/telemac_3d_sample/telemac_3d.slf")

@pytest.fixture
def point_data():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="ELEVATION Z", unit="M", type="SCALAR")
    data.append(name="VELOCITY U", unit="M/S", type="SCALAR")
    data.append(name="VELOCITY V", unit="M/S", type="SCALAR")
    data.append(name="VELOCITY W", unit="M/S", type="SCALAR")

    return data

def test_create_streaming_sequence_telemac_3d(preview_object, point_data):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(5)

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max=10, length=10, name="My_TELEMAC_Streaming_Sim_3D",
               module='TELEMAC', shade_smooth=True)

    assert state == {'FINISHED'}

    # Get sequence
    sequence = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_3D_sequence", None)
    # Check streaming sequence object
    assert sequence is not None
    assert len(sequence.children) == 3

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data.dumps()


def test_streaming_sequence_telemac_3d(streaming_sequence, frame_change_pre, point_data):
    # Force update telemac streaming sequences
    handler = frame_change_pre("update_telemac_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert streaming_sequence.tbb.uid != ""
    assert streaming_sequence.tbb.module == 'TELEMAC'
    assert streaming_sequence.tbb.is_mesh_sequence is False
    assert streaming_sequence.tbb.is_streaming_sequence is True
    assert streaming_sequence.tbb.settings.file_path == FILE_PATH

    # Test streaming sequence settings
    sequence = streaming_sequence.tbb.settings.telemac.s_sequence
    assert sequence is not None

    assert sequence.update is True
    assert sequence.start == 0
    assert sequence.max == 10
    assert sequence.length == 10

    # Disable updates for this sequence object during the next tests
    sequence.update = False


def test_geometry_streaming_sequence_telemac_3d(streaming_sequence):
    # Test geometry
    for obj in streaming_sequence.children:
        assert len(obj.data.edges) == 13601
        assert len(obj.data.vertices) == 4624
        assert len(obj.data.polygons) == 8978


def test_point_data_streaming_sequence_telemac_3d(streaming_sequence, get_mean_value):
    spmv = [0, 0, 0, 0]

    for child in streaming_sequence.children:
        vertex_colors = child.data.vertex_colors
        # Check number vertex colors arrays
        assert len(vertex_colors) == 2

        data = vertex_colors.get("ELEVATION Z, VELOCITY U, VELOCITY V", None)
        assert data is not None

        spmv[0] += get_mean_value(data, child, 0)
        spmv[1] += get_mean_value(data, child, 1)
        spmv[2] += get_mean_value(data, child, 2)

        data = vertex_colors.get("VELOCITY W, None, None", None)
        assert data is not None

        spmv[3] += get_mean_value(data, child, 0)

    assert np.abs(spmv[0] - 1.3966979898702376) < utils.PDV_THRESHOLD
    assert np.abs(spmv[1] - 1.499999413975607) < utils.PDV_THRESHOLD
    assert np.abs(spmv[2] - 1.499999413975607) < utils.PDV_THRESHOLD
    assert np.abs(spmv[3] - 0.818980118090674) < utils.PDV_THRESHOLD


def test_create_mesh_sequence_telemac_3d(preview_object):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 8
    bpy.context.scene.frame_set(8)

    op = bpy.ops.tbb.telemac_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=0, max=10, end=6, name="My_TELEMAC_Sim_3D", mode='TEST')
    assert state == {'FINISHED'}


def test_mesh_sequence_telemac_3d(mesh_sequence, frame_change_post, point_data):
    # Check mesh sequence object
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 3

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 13
    bpy.context.scene.frame_set(13)

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data[mesh_sequence.tbb.uid]
    assert file_data is not None

    # Add point data settings
    mesh_sequence.tbb.settings.point_data.import_data = True
    mesh_sequence.tbb.settings.point_data.list = point_data.dumps()

    # Force update telemac mesh sequences
    handler = frame_change_post("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert mesh_sequence.tbb.uid != ""
    assert mesh_sequence.tbb.module == 'TELEMAC'
    assert mesh_sequence.tbb.is_mesh_sequence is True
    assert mesh_sequence.tbb.is_streaming_sequence is False
    assert mesh_sequence.tbb.settings.file_path == FILE_PATH

    # Test sequence data
    for child in mesh_sequence.children:
        assert len(child.data.shape_keys.key_blocks) == 6

    # Disable updates for this sequence object during the next tests
    mesh_sequence.tbb.settings.point_data.import_data = False


def test_geometry_mesh_sequence_telemac_3d(mesh_sequence):
    # Test geometry
    for child in mesh_sequence.children:
        assert len(child.data.edges) == 13601
        assert len(child.data.vertices) == 4624
        assert len(child.data.polygons) == 8978


def test_point_data_mesh_sequence_telemac_3d(mesh_sequence, get_mean_value):
    spmv = [0, 0, 0, 0]

    for child in mesh_sequence.children:
        vertex_colors = child.data.vertex_colors
        # Check number vertex colors arrays
        assert len(vertex_colors) == 2

        data = vertex_colors.get("ELEVATION Z, VELOCITY U, VELOCITY V", None)
        assert data is not None

        spmv[0] += get_mean_value(data, child, 0)
        spmv[1] += get_mean_value(data, child, 1)
        spmv[2] += get_mean_value(data, child, 2)

        data = vertex_colors.get("VELOCITY W, None, None", None)
        assert data is not None

        spmv[3] += get_mean_value(data, child, 0)

    assert np.abs(spmv[0] - 1.3966979898702376) < utils.PDV_THRESHOLD
    assert np.abs(spmv[1] - 1.499999413975607) < utils.PDV_THRESHOLD
    assert np.abs(spmv[2] - 1.499999413975607) < utils.PDV_THRESHOLD
    assert np.abs(spmv[3] - 0.818980118090674) < utils.PDV_THRESHOLD


def test_extract_point_data_telemac_3d(preview_object, point_data):
    op = bpy.ops.tbb.telemac_extract_point_data

    # Get test data
    data = json.dumps(point_data.get('VELOCITY V'))

    # Note: Fudaa count indices from 1 to xxx. Here we count indices from 0 to xxx.
    state = op('EXEC_DEFAULT', mode='TEST', vertex_id=3007 - 1, max=10, start=0, end=10, test_data=data, plane_id=1)
    assert state == {'FINISHED'}

    # Test keyframes
    assert len(preview_object.animation_data.action.fcurves) == 1
    fcurve = preview_object.animation_data.action.fcurves[0]
    assert fcurve.data_path == '["VELOCITY V"]'
    assert fcurve.range()[0] == 0.0
    assert fcurve.range()[1] == 10.0

    # Test extracted values
    ground_truth = open(os.path.abspath("./data/telemac_3d_sample/point_data_2_3007.csv"), "r")

    for line, id in zip(ground_truth.readlines(), range(-1, 11, 1)):
        if 'VELOCITY V' not in line:
            value = float(line.split(";")[-1][:-1])

            # ------------------------------------------------------------ #
            # /!\ WARNING: next tests are based on the following frame /!\ #
            # ------------------------------------------------------------ #
            # Change frame to load time point 'id'
            bpy.context.scene.frame_set(id)

            assert id == bpy.context.scene.frame_current
            assert np.abs(preview_object["VELOCITY V"] - value) < utils.PDV_THRESHOLD

    ground_truth.close()
