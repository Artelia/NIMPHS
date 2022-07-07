# <pep8 compliant>
import os
import bpy
import json
import pytest
import numpy as np

# Sample 2D:
#   Number of variables = 6

#   Variables:
#                     (Time point = 5, remapped)    (GLOBAL)                        (GLOBAL)
#   VELOCITY U:       mean = 0.2148579548180691     min = 0.0                       max = 2.7853646278381348  (M/S)
#   VELOCITY V:       mean = 0.4044774340143149     min = -0.40747132897377014      max = 0.5237767696380615  (M/S)
#   WATER DEPTH:      mean = 0.5031066531588434     min = 0.0                       max = 1.0                 (M)
#   ANALYTIC SOL H:   mean = 0.5015619112950673     min = 0.0                       max = 1.0                 (NONE)
#   ANALYTIC SOL U:   mean = 0.36766125498385516    min = 0.0                       max = 6.254727840423584   (NONE)
#   ANALYTIC SOL V:   mean = 1.0                    min = 0.0                       max = 0.0                 (NONE)

#   IS 3D = False
#   NB PLANES = 0
#   NB TIME POINTS = 11
#   MESH: Vertices = 3,200 | Edges = 8,941 | Faces = 5,742 | Triangles = 5,742

FILE_PATH = os.path.abspath("./data/telemac_2d_sample/telemac_2d.slf")
# Point data value threshold for tests
PDV_THRESHOLD = 0.01


@pytest.fixture
def mesh_sequence():
    return bpy.data.objects.get("My_TELEMAC_Sim_2D_sequence", None)


@pytest.fixture
def streaming_sequence():
    return bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)


@pytest.fixture
def preview_object():
    obj = bpy.data.objects.get("TBB_TELEMAC_preview_2D", None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj


@pytest.fixture
def point_data_test():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="VELOCITY U", unit="M/S", type="SCALAR")
    data.append(name="VELOCITY V", unit="M/S", type="SCALAR")
    data.append(name="WATER DEPTH", unit="M", type="SCALAR")
    data.append(name="ANALYTIC SOL H", unit="NONE", type="SCALAR")
    data.append(name="ANALYTIC SOL U", unit="NONE", type="SCALAR")
    data.append(name="ANALYTIC SOL V", unit="NONE", type="SCALAR")

    return data


@pytest.fixture
def get_mean_value():
    from bpy.types import Object, MeshLoopColorLayer

    def mean_value(colors: MeshLoopColorLayer, obj: Object, channel: int):
        data = [0] * len(obj.data.loops) * 4
        colors.data.foreach_get("color", data)
        extracted = [data[i] for i in range(channel, len(data), 4)]
        return np.sum(extracted) / len(obj.data.loops)

    return mean_value


@pytest.fixture
def frame_change_post():

    def get_handler(name: str):
        for handler in bpy.app.handlers.frame_change_post:
            if handler.__name__ == name:
                return handler

        return None

    return get_handler


@pytest.fixture
def frame_change_pre():

    def get_handler(name: str):
        for handler in bpy.app.handlers.frame_change_pre:
            if handler.__name__ == name:
                return handler

        return None

    return get_handler


def test_import_telemac_2d():
    op = bpy.ops.tbb.import_telemac_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="here.slf", name="TBB_TELEMAC_preview_2D") == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=FILE_PATH, name="TBB_TELEMAC_preview_2D") == {"FINISHED"}


def test_geometry_imported_object_telemac_2d(preview_object):
    # Check imported object
    assert preview_object is not None
    assert len(preview_object.children) == 2

    # Test geometry
    for child in preview_object.children:
        assert len(child.data.vertices) == 3200
        assert len(child.data.edges) == 8941
        assert len(child.data.polygons) == 5742


def test_reload_file_data_telemac_2d(preview_object):
    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test file data
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None
    assert file_data.nb_vars == 6
    assert file_data.nb_planes == 0
    assert file_data.vars is not None
    assert file_data.is_3d() is False
    assert file_data.faces is not None
    assert file_data.module == "TELEMAC"
    assert file_data.nb_time_points == 11
    assert file_data.vertices is not None
    assert file_data.nb_vertices == 3200
    assert file_data.nb_triangles == 5742


def test_preview_telemac_2d(preview_object, point_data_test):
    # Set preview settings
    preview_object.tbb.settings.preview_time_point = 5
    preview_object.tbb.settings.preview_point_data = json.dumps(point_data_test.get("VELOCITY U"))

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_preview_object_telemac_2d(preview_object):
    # Check preview object
    assert preview_object is not None
    assert len(preview_object.children) == 2

    # Test geometry
    for child in preview_object.children:
        assert len(child.data.edges) == 8941
        assert len(child.data.vertices) == 3200
        assert len(child.data.polygons) == 5742


def test_point_data_preview_object_telemac_2d(preview_object, get_mean_value):
    for child in preview_object.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        vitesse_u = vertex_colors.get("VELOCITY U, None, None", None)
        assert vitesse_u is not None

        # Test point data values (compare mean values, less than .1% of difference is ok)
        assert np.abs(get_mean_value(vitesse_u, child, 0) - 0.2148579548180691) < PDV_THRESHOLD


def test_compute_ranges_point_data_values_telemac_2d(preview_object, point_data_test):
    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=point_data_test.dumps()) == {'FINISHED'}

    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    fond = file_data.vars.get("VELOCITY U", prop='RANGE')["global"]
    assert fond["min"] == 0.0 and fond["max"] == 2.7853646278381348

    vitesse_u = file_data.vars.get("VELOCITY V", prop='RANGE')["global"]
    assert vitesse_u["min"] == -0.40747132897377014 and vitesse_u["max"] == 0.5237767696380615

    vitesse_v = file_data.vars.get("WATER DEPTH", prop='RANGE')["global"]
    assert vitesse_v["min"] == 0.0 and vitesse_v["max"] == 1.0

    salinite = file_data.vars.get("ANALYTIC SOL H", prop='RANGE')["global"]
    assert salinite["min"] == 0.0 and salinite["max"] == 1.0

    hauteur_eau = file_data.vars.get("ANALYTIC SOL U", prop='RANGE')["global"]
    assert hauteur_eau["min"] == 0.0 and hauteur_eau["max"] == 6.254727840423584

    surface_libre = file_data.vars.get("ANALYTIC SOL V", prop='RANGE')["global"]
    assert surface_libre["min"] == 0.0 and surface_libre["max"] == 0.0


def test_create_streaming_sequence_telemac_2d(preview_object, point_data_test):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(5)

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max=11, length=11, name="My_TELEMAC_Streaming_Sim_2D",
               module='TELEMAC', shade_smooth=True)

    assert state == {"FINISHED"}

    # Get sequence
    sequence = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)
    # Check streaming sequence object
    assert sequence is not None
    assert len(sequence.children) == 2

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data_test.dumps()


def test_streaming_sequence_telemac_2d(streaming_sequence, frame_change_pre, point_data_test):
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

        assert np.abs(get_mean_value(data, child, 0) - 0.2148579548180691) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.4044774340143149) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 0.5031066531588434) < PDV_THRESHOLD

        data = vertex_colors.get("ANALYTIC SOL H, ANALYTIC SOL U, ANALYTIC SOL V", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.5015619112950673) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.36766125498385516) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 1.0) < PDV_THRESHOLD


def test_create_mesh_sequence_telemac_2d(preview_object):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 8
    bpy.context.scene.frame_set(8)

    op = bpy.ops.tbb.telemac_create_mesh_sequence
    state = op('EXEC_DEFAULT', mode='TEST', start=0, max=11, end=6, name="My_TELEMAC_Sim_2D")
    assert state == {"FINISHED"}


def test_mesh_sequence_telemac_2d(mesh_sequence, frame_change_post, point_data_test):
    # Check sequence object
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

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
    mesh_sequence.tbb.settings.point_data.list = point_data_test.dumps()

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

    # Test sequence data (shape_keys)
    for child in mesh_sequence.children:
        assert len(child.data.shape_keys.key_blocks) == 6

    # Disable updates for this sequence object during the next tests
    mesh_sequence.tbb.settings.point_data.import_data = False


def test_geometry_mesh_sequence_telemac_2d(mesh_sequence):
    # Test geometry
    for child in mesh_sequence.children:
        assert len(child.data.edges) == 8941
        assert len(child.data.vertices) == 3200
        assert len(child.data.polygons) == 5742


def test_point_data_mesh_sequence_telemac_2d(mesh_sequence, get_mean_value):
    for child in mesh_sequence.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 2

        # Test point data values
        data = vertex_colors.get("VELOCITY U, VELOCITY V, WATER DEPTH", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.2148579548180691) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.4044774340143149) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 0.5031066531588434) < PDV_THRESHOLD

        data = vertex_colors.get("ANALYTIC SOL H, ANALYTIC SOL U, ANALYTIC SOL V", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.5015619112950673) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 1) - 0.36766125498385516) < PDV_THRESHOLD
        assert np.abs(get_mean_value(data, child, 2) - 1.0) < PDV_THRESHOLD


def test_extract_point_data_telemac_2d(preview_object, point_data_test):
    op = bpy.ops.tbb.telemac_extract_point_data

    # Get test data
    data = json.dumps(point_data_test.get('SALINITE'))

    # Note: Fudaa count indices from 1 to xxx. Here we count indices from 0 to xxx.
    state = op('EXEC_DEFAULT', mode='TEST', vertex_id=1526 - 1, max=30, start=0, end=30, test_data=data)
    assert state == {'FINISHED'}

    # Test keyframes
    assert len(preview_object.animation_data.action.fcurves) == 1
    fcurve = preview_object.animation_data.action.fcurves[0]
    assert fcurve.data_path == '["SALINITE"]'
    assert fcurve.range()[0] == 0.0
    assert fcurve.range()[1] == 30.0

    # Test extracted values
    ground_truth = open(os.path.abspath("./data/telemac_2d_sample/telemac_2d_salinite_1526.csv"), "r")

    for line, id in zip(ground_truth.readlines(), range(-1, 31, 1)):
        if 'SALINITE' not in line:
            value = float(line.split(";")[-1][:-1])

            # ------------------------------------------------------------ #
            # /!\ WARNING: next tests are based on the following frame /!\ #
            # ------------------------------------------------------------ #
            # Change frame to load time point 'id'
            bpy.context.scene.frame_set(id)

            assert id == bpy.context.scene.frame_current
            assert np.abs(preview_object["SALINITE"] - value) < 0.001

    ground_truth.close()
