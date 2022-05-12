import os
import bpy
import time

# Sample A:
# Number of time points = 21
# Raw mesh: Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092
# Triangulated mesh: Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092


def test_load_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    tmp_data = bpy.context.scene.tbb.settings.openfoam.tmp_data
    # Verify default parameters
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21


def test_reload_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    assert bpy.ops.tbb.reload_openfoam_file('EXEC_DEFAULT') == {"FINISHED"}
    # TODO: Test tmp data


def test_preview_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}
    # TODO: Test preview object and preview material


def test_create_streaming_sequence_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    settings = bpy.context.scene.tbb.settings.openfoam
    # Clip settings
    settings.clip.type = 'scalar'
    settings.clip.scalar.name = 'alpha.water@value'
    settings.clip.scalar.value = 0.5
    # Sequence settings
    settings.sequence_type = "streaming_sequence"
    settings.frame_start = 1
    settings["anim_length"] = 21
    settings.import_point_data = True
    settings.list_point_data = "U;alpha.water;p;p_rgh"
    settings.sequence_name = "My_OpenFOAM_Streaming_Sim"
    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT') == {"FINISHED"}

    # Test settings of the created sequence
    seq_obj = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert seq_obj is not None
    assert seq_obj.tbb.is_streaming_sequence == True
    seq_settings = seq_obj.tbb.settings.openfoam.streaming_sequence
    # Common settings
    assert seq_settings.name == "My_OpenFOAM_Streaming_Sim_sequence"
    assert seq_settings.update == True
    assert seq_settings.file_path == path
    assert seq_settings.frame_start == 1
    assert seq_settings.max_length == 21
    assert seq_settings.anim_length == 21
    assert seq_settings.import_point_data == True
    assert seq_settings.list_point_data == "U;alpha.water;p;p_rgh"
    # OpenFOAM settings
    assert seq_settings.decompose_polyhedra == False
    assert seq_settings.triangulate == True
    assert seq_settings.clip.type == 'scalar'
    assert seq_settings.clip.scalar.value == 0.5
    assert seq_settings.clip.scalar.name == "alpha.water@value"
    assert seq_settings.clip.scalar.invert == False

    # TODO: Test geometry and impoted point data


# WARNING: This test can take a while but pytest won't see it since the operator is running modal (on timer event)
# This can cause some context issues ('create_sequence_is_running' will probably be set to 'true')
def test_create_mesh_sequence_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=path) == {"FINISHED"}

    settings = bpy.context.scene.tbb.settings.openfoam
    # Clip settings
    settings.clip.type = 'scalar'
    settings.clip.scalar.name = 'alpha.water@value'
    settings.clip.scalar.value = 0.5
    # Sequence settings
    settings.sequence_type = "mesh_sequence"
    settings["start_time_point"] = 0
    settings["end_time_point"] = 5
    settings.import_point_data = True
    settings.list_point_data = "U;alpha.water;p;p_rgh"
    settings.sequence_name = "My_OpenFOAM_Sim"
    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}

    # TODO: Test geometry and impoted point data
