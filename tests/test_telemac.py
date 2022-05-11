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
    assert not tmp_data.is_3d


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
    assert tmp_data.is_3d
