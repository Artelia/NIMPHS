import os
import bpy

# Sample A:
# Number of time points = 21
# Raw mesh: Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092
# Triangulated mesh: Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092


def test_load_openfoam():
    path = os.path.abspath("./data/openfoam_sample_a/foam.foam")
    bpy.ops.tbb.import_openfoam_file('INVOKE_DEFAULT', filepath=path)

    tmp_data = bpy.context.scene.tbb.settings.openfoam.tmp_data
    # Verify default parameters
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21
