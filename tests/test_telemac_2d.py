# <pep8 compliant>
import os
import bpy
import json
import pytest

# Sample 2D:
# Number of variables = 8
# (FOND, VITESSE U, VITESSE V, SALINITE, HAUTEUR D'EAU, SURFACE LIBRE, DEBIT SOL EN X, DEBIT SOL EN Y)
# Number of planes = 0
# Is not from a 3D simulation
# Number of time points = 31
# Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199

FILE_PATH = os.path.abspath("./data/telemac_sample_2d.slf")


@pytest.fixture
def preview_object():
    obj = bpy.data.objects.get("TBB_TELEMAC_preview", None)
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


def test_import_telemac_2d():
    op = bpy.ops.tbb.import_telemac_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="here.slf") == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}


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

    # Test temporary data
    tmp_data = bpy.context.scene.tbb.tmp_data[preview_object.tbb.uid]
    assert tmp_data is not None
    assert tmp_data.module_name == "TELEMAC"
    assert tmp_data.vertices is not None
    assert tmp_data.faces is not None
    assert tmp_data.nb_vars == 8
    assert tmp_data.nb_time_points == 31
    assert tmp_data.vars_info is not None
    assert tmp_data.nb_planes == 0
    assert tmp_data.nb_vertices == 12506
    assert tmp_data.nb_triangles == 24199
    assert tmp_data.is_3d is False


def test_preview_telemac_2d(preview_object):
    # Set preview settings
    tmp_data = bpy.context.scene.tbb.tmp_data[preview_object.tbb.uid]
    preview_object.tbb.settings.preview_point_data = json.dumps(tmp_data.vars_info.get(0))

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


def test_create_streaming_sequence_telemac_2d(preview_object):
    # Get temporary data
    tmp_data = bpy.context.scene.tbb.tmp_data[preview_object.tbb.uid]
    preview_object.tbb.settings.preview_point_data = json.dumps(tmp_data.vars_info.get(0))

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=31, length=31, name="My_TELEMAC_Streaming_Sim_2D",
               module='TELEMAC', shade_smooth=True)

    assert state == {"FINISHED"}

    # Get sequence
    sequence = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_2D_sequence", None)
    assert sequence is not None

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = json.dumps(tmp_data.vars_info.get(0))


def test_streaming_sequence_telemac_2d(streaming_sequence, frame_change_pre):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Force update telemac streaming sequences
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
    tmp_data = bpy.context.scene.tbb.tmp_data[streaming_sequence.tbb.uid]
    assert streaming_sequence.tbb.settings.point_data.import_data is True
    assert streaming_sequence.tbb.settings.point_data.list == json.dumps(tmp_data.vars_info.get(0))

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

    # Force update telemac mesh sequences
    handler = frame_change_post("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test sequence object
    assert mesh_sequence.tbb.settings.telemac.is_mesh_sequence is True
    assert mesh_sequence.tbb.uid != ""
    sequence = mesh_sequence.tbb.settings.telemac.mesh_sequence
    assert sequence is not None
    assert sequence.import_point_data is True
    assert sequence.point_data == "VITESSE U;SALINITE;VITESSE V;FOND;"
    assert sequence.file_path == FILE_PATH
    assert sequence.is_3d_simulation is False

    # Disable updates for this sequence object during the next tests
    mesh_sequence.tbb.settings.telemac.mesh_sequence.import_point_data = False

    # Test sequence data
    for obj in mesh_sequence.children:
        assert len(obj.data.shape_keys.key_blocks) == 5


def test_geometry_mesh_sequence_telemac_2d(mesh_sequence):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Test geometry
    for obj in mesh_sequence.children:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_mesh_sequence_telemac_2d(mesh_sequence):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Test point data (only test if they exist)
    # TODO: add this, not implemented yet
    for obj in mesh_sequence.children:
        vertex_colors = obj.data.vertex_colors
        assert len(vertex_colors) == 2
        vu_s_vv_colors = vertex_colors.get("VITESSE U, SALINITE, VITESSE V", None)
        assert vu_s_vv_colors is not None
        f_colors = vertex_colors.get("FOND, None, None", None)
        assert f_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])
