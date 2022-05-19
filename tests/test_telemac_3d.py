# <pep8 compliant>
import os
import bpy

# Sample A:
# Number of variables = 6
# Number of planes = 16
# Is not from a 3D simulation
# Number of time points = 31
# Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199

FILE_PATH = os.path.abspath("./data/telemac_sample_b.slf")


def test_import_telemac_3d():
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}

    # Test temporary data default parameters
    tmp_data = bpy.context.scene.tbb.settings.telemac.tmp_data
    assert tmp_data is not None
    assert tmp_data.module_name == "TELEMAC"
    assert tmp_data.file is not None
    assert tmp_data.vertices is not None
    assert tmp_data.faces is not None
    assert tmp_data.nb_vars == 6
    assert tmp_data.nb_time_points == 31
    assert tmp_data.vars_info is not None
    assert tmp_data.nb_planes == 16
    assert tmp_data.nb_vertices == 12506
    assert tmp_data.nb_triangles == 24199
    assert tmp_data.is_3d == True


def test_geometry_imported_preview_object_telemac_3d():
    prw_obj = [bpy.data.objects.get("TBB_TELEMAC_preview_plane_" + str(i), None) for i in range(16)]
    assert None not in prw_obj
    assert len(prw_obj) == 16

    # Test geometry
    for obj in prw_obj:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_reload_telemac_3d():
    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test temporary data
    tmp_data = bpy.context.scene.tbb.settings.telemac.tmp_data
    assert tmp_data is not None
    assert tmp_data.module_name == "TELEMAC"
    assert tmp_data.file is not None
    assert tmp_data.vertices is not None
    assert tmp_data.faces is not None
    assert tmp_data.nb_vars == 6
    assert tmp_data.nb_time_points == 31
    assert tmp_data.vars_info is not None
    assert tmp_data.nb_planes == 16
    assert tmp_data.nb_vertices == 12506
    assert tmp_data.nb_triangles == 24199
    assert tmp_data.is_3d == True


def test_preview_telemac_3d():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.telemac
    settings.normalize_preview_obj = False
    settings.preview_point_data = '1'

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_preview_object_telemac_3d():
    prw_obj = [bpy.data.objects.get("TBB_TELEMAC_preview_plane_" + str(i), None) for i in range(16)]
    assert None not in prw_obj
    assert len(prw_obj) == 16

    # Test geometry
    for obj in prw_obj:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_preview_object_telemac_3d():
    prw_obj = [bpy.data.objects.get("TBB_TELEMAC_preview_plane_" + str(i), None) for i in range(16)]
    assert None not in prw_obj
    assert len(prw_obj) == 16

    # Test point data (only test if they exist)
    for obj in prw_obj:
        vertex_colors = obj.data.vertex_colors
        assert len(vertex_colors) == 1
        u_colors = vertex_colors.get("VITESSE U, None, None", None)
        assert u_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_normalize_preview_telemac_3d():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.telemac
    settings.normalize_preview_obj = True
    settings.preview_point_data = '0'

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_dimensions_normalized_preview_object_telemac_3d():
    prw_obj = [bpy.data.objects.get("TBB_TELEMAC_preview_plane_" + str(i), None) for i in range(16)]
    assert None not in prw_obj
    assert len(prw_obj) == 16

    # Test dimensions
    for obj in prw_obj:
        assert obj.dimensions[0] <= 1.0 and obj.dimensions[1] <= 1.0 and obj.dimensions[2] <= 1.0


def test_create_streaming_sequence_telemac_3d():
    # Set sequence settings
    settings = bpy.context.scene.tbb.settings.telemac
    settings.sequence_name = "My_TELEMAC_Streaming_Sim_3D"
    settings.import_point_data = True
    settings.list_point_data = "VITESSE U;SALINITE;VITESSE V;FOND;"
    settings.frame_start = 1
    settings.anim_length = 31
    settings.sequence_type = "streaming_sequence"

    assert bpy.ops.tbb.telemac_create_sequence('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_streaming_sequence_telemac_3d():
    seq_obj = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_3D_sequence", None)
    assert seq_obj is not None
    assert len(seq_obj.children) == 16

    # Change frame to load another time point for the streaming sequence
    bpy.context.scene.frame_set(21)
    # Disable updates for this sequence object during the next tests
    seq_obj.tbb.settings.telemac.streaming_sequence.update = False

    # Test geometry
    for obj in seq_obj.children:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_streaming_sequence_telemac_3d():
    seq_obj = bpy.data.objects.get("My_TELEMAC_Streaming_Sim_3D_sequence", None)
    assert seq_obj is not None
    assert len(seq_obj.children) == 16

    # Test point data (only test if they exist)
    # TODO: fix this, it is not working ...
    # for obj in seq_obj.children:
    #     vertex_colors = obj.data.vertex_colors
    #     assert len(vertex_colors) == 2
    #     vu_s_vv_colors = vertex_colors.get("VITESSE U, SALINITE, VITESSE V", None)
    #     assert vu_s_vv_colors is not None
    #     f_colors = vertex_colors.get("FOND, None, None", None)
    #     assert f_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_create_mesh_sequence_telemac_3d():
    # Set sequence settings
    settings = bpy.context.scene.tbb.settings.telemac
    settings.sequence_type = "mesh_sequence"
    settings["start_time_point"] = 0
    settings["end_time_point"] = 3
    settings.import_point_data = True
    settings.list_point_data = "VITESSE U;VITESSE V;SALINITE"
    settings.sequence_name = "My_TELEMAC_Sim_3D"

    assert bpy.ops.tbb.telemac_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}


def test_mesh_sequence_telemac_3d():
    seq_obj = bpy.data.objects.get("My_TELEMAC_Sim_3D_sequence", None)
    assert seq_obj is not None
    assert len(seq_obj.children) == 16

    # Change frame to load another time point for the mesh sequence
    bpy.context.scene.frame_set(2)

    # Test sequence data
    for obj in seq_obj.children:
        assert len(obj.data.shape_keys.key_blocks) == 3


def test_geometry_mesh_sequence_telemac_3d():
    seq_obj = bpy.data.objects.get("My_TELEMAC_Sim_3D_sequence", None)
    assert seq_obj is not None
    assert len(seq_obj.children) == 16

    # Test geometry
    for obj in seq_obj.children:
        assert len(obj.data.vertices) == 12506
        assert len(obj.data.edges) == 36704
        assert len(obj.data.polygons) == 24199


def test_point_data_mesh_sequence_telemac_3d():
    seq_obj = bpy.data.objects.get("My_TELEMAC_Sim_3D_sequence", None)
    assert seq_obj is not None
    assert len(seq_obj.children) == 16

    # Test point data (only test if they exist)
    # TODO: add this, not implemented yet
    # for obj in seq_obj.children:
    #     vertex_colors = obj.data.vertex_colors
    #     assert len(vertex_colors) == 2
    #     vu_s_vv_colors = vertex_colors.get("VITESSE U, SALINITE, VITESSE V", None)
    #     assert vu_s_vv_colors is not None
    #     f_colors = vertex_colors.get("FOND, None, None", None)
    #     assert f_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])
