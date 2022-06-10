# <pep8 compliant>
import os
import bpy
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
def scene_settings():
    return bpy.context.scene.tbb.settings.telemac


@pytest.fixture
def preview_object():
    return [bpy.data.objects.get("TBB_TELEMAC_preview_" + type.lower(), None) for type in ['BOTTOM', 'WATER_DEPTH']]


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


def test_import_telemac_2d(scene_settings):
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}

    # Change frame to load another time point for the mesh sequence
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(1)

    # Test temporary data default parameters
    tmp_data = scene_settings.tmp_data
    assert tmp_data is not None
    assert tmp_data.module_name == "TELEMAC"
    assert tmp_data.file is not None
    assert tmp_data.vertices is not None
    assert tmp_data.faces is not None
    assert tmp_data.nb_vars == 8
    assert tmp_data.nb_time_points == 31
    assert tmp_data.vars_info is not None
    assert tmp_data.nb_planes == 0
    assert tmp_data.nb_vertices == 12506
    assert tmp_data.nb_triangles == 24199
    assert tmp_data.is_3d is False


def test_geometry_imported_preview_object_telemac_2d(preview_object):
    assert None not in preview_object
    assert len(preview_object) == 2

    # Test geometry
    for obj in preview_object:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_reload_telemac_2d(scene_settings):
    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test temporary data
    tmp_data = scene_settings.tmp_data
    assert tmp_data is not None
    assert tmp_data.module_name == "TELEMAC"
    assert tmp_data.file is not None
    assert tmp_data.vertices is not None
    assert tmp_data.faces is not None
    assert tmp_data.nb_vars == 8
    assert tmp_data.nb_time_points == 31
    assert tmp_data.vars_info is not None
    assert tmp_data.nb_planes == 0
    assert tmp_data.nb_vertices == 12506
    assert tmp_data.nb_triangles == 24199
    assert tmp_data.is_3d is False


def test_preview_telemac_2d(scene_settings):
    # Set preview settings
    scene_settings.normalize_preview_obj = False
    scene_settings.preview_point_data = '0'

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_preview_object_telemac_2d(preview_object):
    assert None not in preview_object
    assert len(preview_object) == 2

    # Test geometry
    for obj in preview_object:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_preview_object_telemac_2d(preview_object):
    assert None not in preview_object
    assert len(preview_object) == 2

    # Test point data (only test if they exist)
    for obj in preview_object:
        vertex_colors = obj.data.vertex_colors
        assert len(vertex_colors) == 1
        u_colors = vertex_colors.get("VITESSE U, None, None", None)
        assert u_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_normalize_preview_telemac_2d(scene_settings):
    # Set preview settings
    scene_settings.normalize_preview_obj = True
    scene_settings.preview_point_data = '0'

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_dimensions_normalized_preview_object_telemac_2d(preview_object):
    assert None not in preview_object
    assert len(preview_object) == 2

    # Test dimensions
    for obj in preview_object:
        assert obj.dimensions[0] <= 1.0 and obj.dimensions[1] <= 1.0 and obj.dimensions[2] <= 1.0


def test_create_streaming_sequence_telemac_2d(scene_settings):
    # Set sequence settings
    scene_settings.sequence_name = "My_TELEMAC_Streaming_Sim_2D"
    scene_settings.import_point_data = True
    scene_settings.point_data = "VITESSE U;SALINITE;VITESSE V;FOND;"
    scene_settings.frame_start = 1
    scene_settings["anim_length"] = 31
    scene_settings.sequence_type = "streaming_sequence"

    assert bpy.ops.tbb.telemac_create_sequence('EXEC_DEFAULT') == {"FINISHED"}


def test_streaming_sequence_telemac_2d(streaming_sequence, frame_change_pre):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Force update telemac streaming sequences
    handler = frame_change_pre("update_telemac_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test streaming sequence settings
    assert streaming_sequence.tbb.is_streaming_sequence
    seq_settings = streaming_sequence.tbb.settings.telemac.streaming_sequence
    assert seq_settings is not None
    assert seq_settings.name == "My_TELEMAC_Streaming_Sim_2D_sequence"
    assert seq_settings.update is True
    assert seq_settings.frame_start == 1
    assert seq_settings.max_length == 31
    assert seq_settings.anim_length == 31
    assert seq_settings.import_point_data is True
    assert seq_settings.point_data == "VITESSE U;SALINITE;VITESSE V;FOND;"

    # Disable updates for this sequence object during the next tests
    streaming_sequence.tbb.settings.telemac.streaming_sequence.update = False


def test_geometry_streaming_sequence_telemac_2d(streaming_sequence):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Test geometry
    for obj in streaming_sequence.children:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_streaming_sequence_telemac_2d(streaming_sequence):
    assert streaming_sequence is not None
    assert len(streaming_sequence.children) == 2

    # Test point data (only test if they exist)
    for obj in streaming_sequence.children:
        vertex_colors = obj.data.vertex_colors
        assert len(vertex_colors) == 2
        vu_s_vv_colors = vertex_colors.get("VITESSE U, SALINITE, VITESSE V", None)
        assert vu_s_vv_colors is not None
        f_colors = vertex_colors.get("FOND, None, None", None)
        assert f_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_create_mesh_sequence_telemac_2d(scene_settings):
    # Set sequence settings
    scene_settings.sequence_type = "mesh_sequence"
    scene_settings["start_time_point"] = 0
    scene_settings["end_time_point"] = 5
    scene_settings.import_point_data = True
    scene_settings.point_data = "VITESSE U;SALINITE;VITESSE V;FOND;"
    scene_settings.sequence_name = "My_TELEMAC_Sim_2D"

    assert bpy.ops.tbb.telemac_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}


def test_mesh_sequence_telemac_2d(mesh_sequence, frame_change_post):
    assert mesh_sequence is not None
    assert len(mesh_sequence.children) == 2

    # Force update telemac mesh sequences
    handler = frame_change_post("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test sequence object
    assert mesh_sequence.tbb.settings.telemac.is_mesh_sequence is True
    assert mesh_sequence.tbb.uid != "None"
    assert mesh_sequence.tbb.tmp_data[mesh_sequence.tbb.uid] is not None
    seq_settings = mesh_sequence.tbb.settings.telemac.mesh_sequence
    assert seq_settings is not None
    assert seq_settings.import_point_data is True
    assert seq_settings.point_data == "VITESSE U;SALINITE;VITESSE V;FOND;"
    assert seq_settings.file_path == FILE_PATH
    assert seq_settings.is_3d_simulation is False

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
