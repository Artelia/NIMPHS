# <pep8 compliant>
import os
import bpy
import json
import pytest
import numpy as np

# Sample 2D:
#   Number of variables = 8

#   Variables:
#                     (Time point = 5, remapped)    (GLOBAL)                        (GLOBAL)
#   FOND:             mean = 0.04131595387433874    min = -5.0                      max = 2.5                 (M)
#   VITESSE U:        mean = 0.7980087919076801     min = -2.861448049545288        max = 0.801839292049408   (M/S)
#   VITESSE V:        mean = 0.564615949978801      min = -0.44414040446281433      max = 0.6261451244354248  (M/S)
#   SALINITE:         mean = 0.37128353934125063    min = -4.410864619220242e-19    max = 35.0                (NONE)
#   HAUTEUR D'EAU:    mean = 0.9557430329482625     min = 0.0                       max = 7.579009532928467   (M)
#   SURFACE LIBRE:    mean = 0.6245944487400504     min = 1.9149115085601807        max = 7.1949639320373535  (M)
#   DEBIT SOL EN X:   mean = 0.7086518611281863     min = -137.33761596679688       max = 94.22285461425781   (M2/S)
#   DEBIT SOL EN Y:   mean = 0.47028401108210977    min = -53.73036575317383        max = 56.772369384765625  (M2/S)

#   Number of planes = 0
#   Is not from a 3D simulation
#   Number of time points = 31
#   Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199

FILE_PATH = os.path.abspath("./data/telemac_sample_2d.slf")


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
    data.append(name="FOND", unit="M", type="SCALAR")
    data.append(name="VITESSE U", unit="M/S", type="SCALAR")
    data.append(name="VITESSE V", unit="M/S", type="SCALAR")
    data.append(name="SALINITE", unit="NONE", type="SCALAR")
    data.append(name="HAUTEUR D'EAU", unit="M", type="SCALAR")
    data.append(name="SURFACE LIBRE", unit="M", type="SCALAR")
    data.append(name="DEBIT SOL EN X", unit="M2/S", type="SCALAR")
    data.append(name="DEBIT SOL EN Y", unit="M2/S", type="SCALAR")

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
        assert len(child.data.vertices) == 12506
        assert len(child.data.edges) == 36704
        assert len(child.data.polygons) == 24199


def test_reload_file_data_telemac_2d(preview_object):
    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test file data
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None
    assert file_data.nb_vars == 8
    assert file_data.nb_planes == 0
    assert file_data.vars is not None
    assert file_data.is_3d() is False
    assert file_data.faces is not None
    assert file_data.module == "TELEMAC"
    assert file_data.nb_time_points == 31
    assert file_data.vertices is not None
    assert file_data.nb_vertices == 12506
    assert file_data.nb_triangles == 24199


def test_preview_telemac_2d(preview_object, point_data_test):
    # Set preview settings
    preview_object.tbb.settings.preview_time_point = 5
    preview_object.tbb.settings.preview_point_data = json.dumps(point_data_test.get("VITESSE U"))

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_preview_object_telemac_2d(preview_object):
    # Check preview object
    assert preview_object is not None
    assert len(preview_object.children) == 2

    # Test geometry
    for child in preview_object.children:
        assert len(child.data.edges) == 36704
        assert len(child.data.vertices) == 12506
        assert len(child.data.polygons) == 24199


def test_point_data_preview_object_telemac_2d(preview_object, get_mean_value):
    for child in preview_object.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        vitesse_u = vertex_colors.get("VITESSE U, None, None", None)
        assert vitesse_u is not None

        # Test point data values (compare mean values, less than .1% of difference is ok)
        assert np.abs(get_mean_value(vitesse_u, child, 0) - 0.7980087919076801) < 0.008


def test_compute_ranges_point_data_values_telemac_2d(preview_object, point_data_test):
    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=point_data_test.dumps()) == {'FINISHED'}

    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    fond = file_data.vars.get("FOND", prop='RANGE')["global"]
    assert fond["min"] == -5.0 and fond["max"] == 2.5

    vitesse_u = file_data.vars.get("VITESSE U", prop='RANGE')["global"]
    assert vitesse_u["min"] == -2.861448049545288 and vitesse_u["max"] == 0.801839292049408

    vitesse_v = file_data.vars.get("VITESSE V", prop='RANGE')["global"]
    assert vitesse_v["min"] == -0.44414040446281433 and vitesse_v["max"] == 0.6261451244354248

    salinite = file_data.vars.get("SALINITE", prop='RANGE')["global"]
    assert salinite["min"] == -4.410864619220242e-19 and salinite["max"] == 35.0

    hauteur_eau = file_data.vars.get("HAUTEUR D'EAU", prop='RANGE')["global"]
    assert hauteur_eau["min"] == 0.0 and hauteur_eau["max"] == 7.579009532928467

    surface_libre = file_data.vars.get("SURFACE LIBRE", prop='RANGE')["global"]
    assert surface_libre["min"] == 1.9149115085601807 and surface_libre["max"] == 7.1949639320373535

    debit_sol_en_x = file_data.vars.get("DEBIT SOL EN X", prop='RANGE')["global"]
    assert debit_sol_en_x["min"] == -137.33761596679688 and debit_sol_en_x["max"] == 94.22285461425781

    debit_sol_en_y = file_data.vars.get("DEBIT SOL EN Y", prop='RANGE')["global"]
    assert debit_sol_en_y["min"] == -53.73036575317383 and debit_sol_en_y["max"] == 56.772369384765625


def test_create_streaming_sequence_telemac_2d(preview_object, point_data_test):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(5)

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=31, length=31, name="My_TELEMAC_Streaming_Sim_2D",
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
    assert sequence.length == 31
    assert sequence.update is True
    assert sequence.max_length == 31

    # Disable updates for this sequence object during the next tests
    sequence.update = False


def test_geometry_streaming_sequence_telemac_2d(streaming_sequence):
    # Test geometry
    for child in streaming_sequence.children:
        assert len(child.data.edges) == 36704
        assert len(child.data.vertices) == 12506
        assert len(child.data.polygons) == 24199


def test_point_data_streaming_sequence_telemac_2d(streaming_sequence, get_mean_value):
    for child in streaming_sequence.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 3

        # Test point data values
        data = vertex_colors.get("FOND, VITESSE U, VITESSE V", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.04131595387433874) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.7980087919076801) < 0.008
        assert np.abs(get_mean_value(data, child, 2) - 0.564615949978801) < 0.008

        data = vertex_colors.get("SALINITE, HAUTEUR D'EAU, SURFACE LIBRE", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.37128353934125063) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.9557430329482625) < 0.008
        assert np.abs(get_mean_value(data, child, 2) - 0.6245944487400504) < 0.008

        data = vertex_colors.get("DEBIT SOL EN X, DEBIT SOL EN Y, None", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.7086518611281863) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.47028401108210977) < 0.008


def test_create_mesh_sequence_telemac_2d(preview_object):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 8
    bpy.context.scene.frame_set(8)

    op = bpy.ops.tbb.telemac_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=21, end=6, name="My_TELEMAC_Sim_2D", mode='TEST')
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
        assert len(child.data.edges) == 36704
        assert len(child.data.vertices) == 12506
        assert len(child.data.polygons) == 24199


def test_point_data_mesh_sequence_telemac_2d(mesh_sequence, get_mean_value):
    for child in mesh_sequence.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 3

        # Test point data values
        data = vertex_colors.get("FOND, VITESSE U, VITESSE V", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.04131595387433874) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.7980087919076801) < 0.008
        assert np.abs(get_mean_value(data, child, 2) - 0.564615949978801) < 0.008

        data = vertex_colors.get("SALINITE, HAUTEUR D'EAU, SURFACE LIBRE", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.37128353934125063) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.9557430329482625) < 0.008
        assert np.abs(get_mean_value(data, child, 2) - 0.6245944487400504) < 0.008

        data = vertex_colors.get("DEBIT SOL EN X, DEBIT SOL EN Y, None", None)
        assert data is not None

        assert np.abs(get_mean_value(data, child, 0) - 0.7086518611281863) < 0.008
        assert np.abs(get_mean_value(data, child, 1) - 0.47028401108210977) < 0.008
