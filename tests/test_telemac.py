import os
import bpy

# Sample A:
# Number of variables = 8
# Number of planes = 0
# Is not from a 3D simulation
# Number of time points = 31
# Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199

# Sample B:
# Number of variables = 6
# Number of planes = 16
# Is not from a 3D simulation
# Number of time points = 31
# Triangulated mesh: Vertices = 12,506 | Edges = 36,704 | Faces = 24,199 | Triangles = 24,199


def test_load_telemac_2d():
    path = os.path.abspath("./data/telemac_sample_a.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    tmp_data = bpy.context.scene.tbb.settings.telemac.tmp_data
    # Verify default parameters
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
    assert tmp_data.is_3d == False


def test_load_telemac_3d():
    path = os.path.abspath("./data/telemac_sample_b.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    tmp_data = bpy.context.scene.tbb.settings.telemac.tmp_data
    # Verify default parameters
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


def test_reload_telemac():
    path = os.path.abspath("./data/telemac_sample_a.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    assert bpy.ops.tbb.reload_telemac_file('EXEC_DEFAULT') == {"FINISHED"}
    # TODO: Test tmp data


def test_preview_telemac_2d():
    path = os.path.abspath("./data/telemac_sample_a.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}
    # TODO: Test preview object and preview material


def test_preview_telemac_3d():
    path = os.path.abspath("./data/telemac_sample_b.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {"FINISHED"}
    # TODO: Test preview object and preview material


def test_create_mesh_sequence_telemac_2d():
    path = os.path.abspath("./data/telemac_sample_a.slf")
    assert bpy.ops.tbb.import_telemac_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    settings = bpy.context.scene.tbb.settings.telemac
    # Sequence settings
    settings.sequence_type = "mesh_sequence"
    settings["start_time_point"] = 0
    settings["end_time_point"] = 5
    settings.import_point_data = True
    settings.list_point_data = "VITESSE U;VITESSE V;SALINITE"
    settings.sequence_name = "My_TELEMAC_Sim"
    assert bpy.ops.tbb.telemac_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}

    # TODO: Test geometry and impoted point data
