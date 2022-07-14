# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import numpy as np

sys.path.append(os.path.abspath("."))  # Make helpers module available in this file
from helpers import utils

FILE_PATH = os.path.abspath("./data/telemac_2d_sample/telemac_2d.slf")


@pytest.fixture
def point_data():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="VELOCITY U", unit="M/S", type="SCALAR")
    data.append(name="VELOCITY V", unit="M/S", type="SCALAR")
    data.append(name="WATER DEPTH", unit="M", type="SCALAR")
    data.append(name="ANALYTIC SOL H", unit="NONE", type="SCALAR")
    data.append(name="ANALYTIC SOL U", unit="NONE", type="SCALAR")
    data.append(name="ANALYTIC SOL V", unit="NONE", type="SCALAR")

    return data


def test_create_streaming_sequence_telemac_2d(preview_object, point_data):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(5)

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max=11, length=11, name="My_TELEMAC_Streaming_Sim_2D",
               module='TELEMAC', shade_smooth=True)

    assert state == {'FINISHED'}

    # Get sequence
    sequence = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)
    # Check streaming sequence object
    assert sequence is not None
    assert len(sequence.children) == 2

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data.dumps()


def test_streaming_sequence_telemac_2d(streaming_sequence, frame_change_pre, point_data):
    # Force update streaming sequences
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

    assert sequence.start == 0
    assert sequence.length == 11
    assert sequence.update is True
    assert sequence.max == 11

    # Disable updates for this sequence object during the next tests
    sequence.update = False


def test_geometry_streaming_sequence_telemac_2d(streaming_sequence):
    # Test geometry
    for child in streaming_sequence.children:
        assert len(child.data.edges) == 8941
        assert len(child.data.vertices) == 3200
        assert len(child.data.polygons) == 5742


def test_point_data_streaming_sequence_telemac_2d(streaming_sequence, get_mean_value):
    for child in streaming_sequence.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 2

        # Test point data values
        data = vertex_colors.get("VELOCITY U, VELOCITY V, WATER DEPTH", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.2148579548180691) < utils.PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.4044774340143149) < utils.PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 0.5031066531588434) < utils.PDV_THRESHOLD

        data = vertex_colors.get("ANALYTIC SOL H, ANALYTIC SOL U, ANALYTIC SOL V", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.5015619112950673) < utils.PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.36766125498385516) < utils.PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 1.0) < utils.PDV_THRESHOLD


def test_extract_point_data_telemac_2d(preview_object, point_data):
    op = bpy.ops.tbb.telemac_extract_point_data

    # Get test data
    data = json.dumps(point_data.get('VELOCITY U'))

    # Note: Fudaa count indices from 1 to xxx. Here we count indices from 0 to xxx.
    state = op('EXEC_DEFAULT', mode='TEST', vertex_id=125 - 1, max=10, start=0, end=10, test_data=data)
    assert state == {'FINISHED'}

    # Test keyframes
    assert len(preview_object.animation_data.action.fcurves) == 1
    fcurve = preview_object.animation_data.action.fcurves[0]
    assert fcurve.data_path == '["VELOCITY U"]'
    assert fcurve.range()[0] == 0.0
    assert fcurve.range()[1] == 10.0

    # Test extracted values
    ground_truth = open(os.path.abspath("./data/telemac_2d_sample/point_data_125.csv"), "r")

    for line, id in zip(ground_truth.readlines(), range(-1, 11, 1)):
        if 'VELOCITY U' not in line:
            value = float(line.split(";")[-1][:-1])

            # ------------------------------------------------------------ #
            # /!\ WARNING: next tests are based on the following frame /!\ #
            # ------------------------------------------------------------ #
            # Change frame to load time point 'id'
            bpy.context.scene.frame_set(id)

            assert id == bpy.context.scene.frame_current
            assert np.abs(preview_object["VELOCITY U"] - value) < utils.PDV_THRESHOLD

    ground_truth.close()
