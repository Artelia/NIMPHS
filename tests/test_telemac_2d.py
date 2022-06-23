# <pep8 compliant>
import os
import bpy
import json
import pytest

# Sample 2D:
#   Number of variables = 8

#   Variables:
#   FOND:             min = -5.0                      max = 2.5
#   VITESSE U:        min = -2.861448049545288        max = 0.801839292049408
#   VITESSE V:        min = -0.44414040446281433      max = 0.6261451244354248
#   SALINITE:         min = -4.410864619220242E-19    max = 35.0
#   HAUTEUR D'EAU:    min = 0.0                       max = 7.579009532928467
#   SURFACE LIBRE:    min = 1.9149115085601807        max = 7.1949639320373535
#   DEBIT SOL EN X:   min = -137.33761596679688       max = 94.22285461425781
#   DEBIT SOL EN Y:   min = -53.73036575317383        max = 56.772369384765625

#   Number of planes = 0
#   Is not from a 3D simulation
#   Number of time points = 31
#   Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199

FILE_PATH = os.path.abspath("./data/telemac_sample_2d.slf")


@pytest.fixture
def preview_object():
    obj = bpy.data.objects.get("TBB_TELEMAC_preview_2D", None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj


@pytest.fixture
def mesh_sequence():
    return bpy.data.objects.get("My_TELEMAC_Sim_2D_sequence", None)


@pytest.fixture
def streaming_sequence():
    return bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)


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


@pytest.fixture
def point_data():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="FOND", type="SCALAR")
    data.append(name="VITESSE U", type="SCALAR")
    data.append(name="VITESSE V", type="SCALAR")
    data.append(name="SALINITE", type="SCALAR")
    data.append(name="HAUTEUR D'EAU", type="SCALAR")
    data.append(name="SURFACE LIBRE", type="SCALAR")
    data.append(name="DEBIT SOL EN X", type="SCALAR")
    data.append(name="DEBIT SOL EN Y", type="SCALAR")

    return data


@pytest.fixture
def point_data_test():
    data = {
        "names": ["VITESSE U"],
        "units": ["M/S"],
        "types": ["SCALAR"],
        "ranges": [{"local": {"min": None, "max": None}, "global": {"min": None, "max": None}}],
        "dimensions": [1]
    }
    return json.dumps(data)


def test_import_telemac_2d():
    op = bpy.ops.tbb.import_telemac_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="here.slf", name="TBB_TELEMAC_preview_2D") == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=FILE_PATH, name="TBB_TELEMAC_preview_2D") == {"FINISHED"}


def test_geometry_imported_preview_object_telemac_2d(preview_object):
    assert preview_object is not None
    assert len(preview_object.children) == 2

    # Test geometry
    for child in preview_object.children:
        assert len(child.data.vertices) == 12506
        assert len(child.data.edges) == 36704
        assert len(child.data.polygons) == 24199


def test_reload_telemac_2d(preview_object):
    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test file data
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None
    assert file_data.module == "TELEMAC"
    assert file_data.vertices is not None
    assert file_data.faces is not None
    assert file_data.nb_vars == 8
    assert file_data.nb_time_points == 31
    assert file_data.vars is not None
    assert file_data.nb_planes == 0
    assert file_data.nb_vertices == 12506
    assert file_data.nb_triangles == 24199
    assert file_data.is_3d() is False


def test_preview_telemac_2d(preview_object):
    # Set preview settings
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    preview_object.tbb.settings.preview_point_data = json.dumps(file_data.vars.get(0))

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_preview_object_telemac_2d(preview_object):
    assert preview_object is not None
    assert len(preview_object.children) == 2

    # Test geometry
    for child in preview_object.children:
        assert len(child.data.vertices) == 12506
        assert len(child.data.edges) == 36704
        assert len(child.data.polygons) == 24199


def test_point_data_preview_object_telemac_2d(preview_object):
    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    for child in preview_object.children:
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1
        data = vertex_colors.get("VITESSE U, None, None", None)
        assert data is not None


def test_compute_ranges_point_data_values(preview_object, point_data):
    # Set point data on which to compute value ranges
    bpy.context.scene.tbb.op_vars = point_data

    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='NORMAL') == {'FINISHED'}

    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test computed values
    variables = file_data.vars
    assert variables.length() == 8

    fond = variables.get("FOND", prop='RANGE')["global"]
    assert fond is not None
    assert fond["min"] == -5.0 and fond["max"] == 2.5

    vitesse_u = variables.get("VITESSE U", prop='RANGE')["global"]
    assert vitesse_u is not None
    assert vitesse_u["min"] == -2.861448049545288 and vitesse_u["max"] == 0.801839292049408


def test_create_streaming_sequence_telemac_2d(preview_object, point_data_test):
    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=31, length=31, name="My_TELEMAC_Streaming_Sim_2D",
               module='TELEMAC', shade_smooth=True)

    assert state == {"FINISHED"}

    # Get sequence
    sequence = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)
    assert sequence is not None

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data_test


def test_streaming_sequence_telemac_2d(streaming_sequence, frame_change_pre, point_data_test):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Force update streaming sequences
    handler = frame_change_pre("update_telemac_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert streaming_sequence.tbb.is_streaming_sequence is True
    assert streaming_sequence.tbb.is_mesh_sequence is False
    assert streaming_sequence.tbb.uid != ""
    assert streaming_sequence.tbb.module == 'TELEMAC'
    assert streaming_sequence.tbb.settings.file_path == FILE_PATH

    # Test streaming sequence settings
    sequence = streaming_sequence.tbb.settings.telemac.s_sequence
    assert sequence is not None
    assert sequence.update is True
    assert sequence.start == 0
    assert sequence.max_length == 31
    assert sequence.length == 31

    # Test point data settings
    assert streaming_sequence.tbb.settings.point_data.import_data is True
    point_data_name = json.loads(streaming_sequence.tbb.settings.point_data.list)["names"][0]
    assert point_data_name == json.loads(point_data_test)["names"][0]

    # Disable updates for this sequence object during the next tests
    sequence.update = False


def test_geometry_streaming_sequence_telemac_2d(streaming_sequence):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Test geometry
    for child in streaming_sequence.children:
        assert len(child.data.vertices) == 12506
        assert len(child.data.edges) == 36704
        assert len(child.data.polygons) == 24199


def test_point_data_streaming_sequence_telemac_2d(streaming_sequence):
    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    for child in streaming_sequence.children:
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1
        data = vertex_colors.get("VITESSE U, None, None", None)
        assert data is not None


def test_create_mesh_sequence_telemac_2d(preview_object):
    # Change frame to create the mesh sequence from another frame
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(9)
    op = bpy.ops.tbb.telemac_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=21, end=4, name="My_TELEMAC_Sim_2D", mode='NORMAL')
    assert state == {"FINISHED"}


def test_mesh_sequence_telemac_2d(mesh_sequence, frame_change_post):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data[mesh_sequence.tbb.uid]
    assert file_data is not None

    # Add point data settings
    mesh_sequence.tbb.settings.point_data.import_data = True
    mesh_sequence.tbb.settings.point_data.list = json.dumps(file_data.vars.get(0))

    # Force update telemac mesh sequences
    handler = frame_change_post("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert mesh_sequence.tbb.is_streaming_sequence is False
    assert mesh_sequence.tbb.is_mesh_sequence is True
    assert mesh_sequence.tbb.uid != ""
    assert mesh_sequence.tbb.module == 'TELEMAC'
    assert mesh_sequence.tbb.settings.file_path == FILE_PATH

    # Test sequence data
    for child in mesh_sequence.children:
        assert len(child.data.shape_keys.key_blocks) == 4


def test_geometry_mesh_sequence_telemac_2d(mesh_sequence):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Test geometry
    for child in mesh_sequence.children:
        assert len(child.data.vertices) == 12506
        assert len(child.data.edges) == 36704
        assert len(child.data.polygons) == 24199


def test_point_data_mesh_sequence_telemac_2d(mesh_sequence):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    for child in mesh_sequence.children:
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1
        data = vertex_colors.get("VITESSE U, None, None", None)
        assert data is not None

    # Disable updates for this sequence object during the next tests
    mesh_sequence.tbb.settings.point_data.import_data = False
