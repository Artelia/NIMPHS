# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import pyvista
import numpy as np

sys.path.append(os.path.abspath("."))  # Make helpers module available in this file
from helpers import utils

FILE_PATH = os.path.abspath("./data/openfoam_sample_a/foam.foam")

@pytest.fixture
def point_data():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="U", type="VECTOR", dim=3)
    data.append(name="alpha.water", type="SCALAR")
    data.append(name="nut", type="SCALAR")

    return data


def test_create_streaming_sequence_openfoam(preview_object, point_data):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 11
    bpy.context.scene.frame_set(11)

    op = bpy.ops.tbb.openfoam_create_streaming_sequence
    state = op('EXEC_DEFAULT', name="My_OpenFOAM_Streaming_Sim", start=1, length=21, max=21, shade_smooth=True)
    assert state == {'FINISHED'}

    # Get and check sequence
    sequence = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert sequence is not None
    assert sequence.tbb.is_streaming_sequence is True

    # Set import settings
    sequence.tbb.settings.openfoam.import_settings.triangulate = True
    sequence.tbb.settings.openfoam.import_settings.skip_zero_time = False
    sequence.tbb.settings.openfoam.import_settings.case_type = 'reconstructed'
    sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra = True

    # Set clip settings
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    sequence.tbb.settings.openfoam.clip.type = 'SCALAR'
    sequence.tbb.settings.openfoam.clip.scalar.value = 0.5
    sequence.tbb.settings.openfoam.clip.scalar.name = json.dumps(file_data.vars.get("alpha.water"))

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data.dumps()


def test_streaming_sequence_openfoam(streaming_sequence, frame_change_pre):
    # Force update streaming sequences
    handler = frame_change_pre("update_openfoam_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Disable updates for this sequence object during the next tests
    streaming_sequence.tbb.settings.openfoam.s_sequence.update = False

    # Test object settings
    streaming_sequence.tbb.settings.file_path == FILE_PATH

    # Test sequence settings
    sequence = streaming_sequence.tbb.settings.openfoam.s_sequence
    # assert sequence.start == 1 # TODO: fix this test.
    assert sequence.length == 21
    assert sequence.update is False
    assert sequence.max == 21

    # Test import settings
    assert streaming_sequence.tbb.settings.openfoam.import_settings.triangulate is True
    assert streaming_sequence.tbb.settings.openfoam.import_settings.skip_zero_time is False
    assert streaming_sequence.tbb.settings.openfoam.import_settings.case_type == 'reconstructed'
    assert streaming_sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra is True

    # Test clip settings
    file_data = bpy.context.scene.tbb.file_data.get(streaming_sequence.tbb.uid, None)
    assert file_data is not None

    assert streaming_sequence.tbb.settings.openfoam.clip.type == 'SCALAR'
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.value == 0.5
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.name == json.dumps(file_data.vars.get("alpha.water"))


def test_geometry_streaming_sequence_openfoam(streaming_sequence):
    # Test geometry (time point 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    assert len(streaming_sequence.data.edges) == 158461
    assert len(streaming_sequence.data.vertices) == 55099
    assert len(streaming_sequence.data.polygons) == 103540


def test_point_data_streaming_sequence_openfoam(streaming_sequence):
    # Check number vertex colors arrays
    vertex_colors = streaming_sequence.data.vertex_colors
    assert len(vertex_colors) == 2

    # Test point data values
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    data = vertex_colors.get("U.x, U.y, U.z", None)
    assert data is not None

    data = vertex_colors.get("alpha.water, nut, None", None)
    assert data is not None
