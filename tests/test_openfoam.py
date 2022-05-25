# <pep8 compliant>
import os
import bpy
import pytest

# Sample A:
# Number of time points = 21
# Non-triangulated mesh: Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092
# Non-triangulated-mesh (decomp. polyh.): Vertices = 60,548 | Edges = 121,748 | Faces = 61,202 | Triangles = 121,092
# Triangulated mesh (w/wo decomp. polyh.): Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092
# Time point 11, clip aplha.water (value = 0.5):
# Vertices = 55,718 | Edges = 159,953 | Faces = 104,450 | Triangles = 104,450

FILE_PATH = os.path.abspath("./data/openfoam_sample_a/foam.foam")


@pytest.fixture
def scene_settings():
    return bpy.context.scene.tbb.settings.openfoam


@pytest.fixture
def preview_object():
    return bpy.data.objects.get("TBB_OpenFOAM_preview", None)


@pytest.fixture
def mesh_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Sim_sequence", None)


@pytest.fixture
def streaming_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)


def test_import_openfoam(scene_settings):
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}

    tmp_data = scene_settings.tmp_data

    # Test temporary data default parameters
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21


def test_geometry_imported_preview_object_openfoam(preview_object):
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092


def test_reload_openfoam(scene_settings):
    assert bpy.ops.tbb.reload_openfoam_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test temporary data parameters
    tmp_data = scene_settings.tmp_data
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21


def test_normal_preview_object_openfoam(scene_settings):
    # Set preview settings
    scene_settings.decompose_polyhedra = False
    scene_settings.triangulate = False
    scene_settings.case_type = 'reconstructed'
    scene_settings.preview_point_data = "alpha.water@value"

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_preview_object(preview_object):
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.edges) == 120428
    assert len(preview_object.data.polygons) == 59882


def test_normal_decompose_polyhedra_preview_object_openfoam(scene_settings):
    # Set preview settings
    scene_settings.decompose_polyhedra = True
    scene_settings.triangulate = False
    scene_settings.case_type = 'reconstructed'
    scene_settings.preview_point_data = "alpha.water@value"

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_decompose_polyhedra_preview_object_openfoam(preview_object):
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.edges) == 121748
    assert len(preview_object.data.polygons) == 61202


def test_triangulated_preview_object_openfoam(scene_settings):
    # Set preview settings
    scene_settings.decompose_polyhedra = False
    scene_settings.triangulate = True
    scene_settings.case_type = 'reconstructed'
    scene_settings.preview_point_data = "alpha.water@value"

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_triangulated_preview_object_openfoam(preview_object):
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092


def test_triangulated_decompose_polyhedra_preview_object_openfoam(scene_settings):
    # Set preview settings
    scene_settings.decompose_polyhedra = True
    scene_settings.triangulate = True
    scene_settings.case_type = 'reconstructed'
    scene_settings.preview_point_data = "alpha.water@value"

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_triangulated_decompose_polyhedra_preview_object_openfoam(preview_object):
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092


def test_point_data_preview_object_openfoam(preview_object):
    assert preview_object is not None

    # Test point data (only test if they exist)
    vertex_colors = preview_object.data.vertex_colors
    assert len(vertex_colors) == 1
    aw_colors = vertex_colors.get("alpha.water, None, None", None)
    assert aw_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_preview_material_openfoam():
    # Test preview material
    prw_mat = bpy.data.materials.get("TBB_OpenFOAM_preview_material", None)
    assert prw_mat is not None
    assert prw_mat.use_nodes == True
    # Test nodes
    principled_bsdf_node = prw_mat.node_tree.nodes.get("Principled BSDF", None)
    assert principled_bsdf_node is not None
    vertex_color_node = prw_mat.node_tree.nodes.get("TBB_OpenFOAM_preview_material_vertex_color", None)
    assert vertex_color_node is not None
    assert vertex_color_node.layer_name == "alpha.water, None, None"
    # Test links
    link = prw_mat.node_tree.links[-1]
    assert link.from_node == vertex_color_node
    assert link.from_socket == vertex_color_node.outputs[0]
    assert link.to_node == principled_bsdf_node
    assert link.to_socket == principled_bsdf_node.inputs[0]


def test_create_streaming_sequence_openfoam(scene_settings):
    # Set file settings
    scene_settings.decompose_polyhedra = True
    scene_settings.triangulate = True
    scene_settings.case_type = 'reconstructed'

    # Set clip settings
    scene_settings.clip.type = 'scalar'
    scene_settings.clip.scalar.name = 'alpha.water@value'
    scene_settings.clip.scalar.value = 0.5

    # Set sequence settings
    scene_settings.sequence_type = "streaming_sequence"
    scene_settings.frame_start = 1
    scene_settings["anim_length"] = 21
    scene_settings.import_point_data = True
    scene_settings.list_point_data = "U;alpha.water;p;p_rgh"
    scene_settings.sequence_name = "My_OpenFOAM_Streaming_Sim"

    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT') == {"FINISHED"}


def test_streaming_sequence_openfoam(streaming_sequence):
    assert streaming_sequence is not None
    assert streaming_sequence.tbb.is_streaming_sequence == True

    # Test common settings
    seq_settings = streaming_sequence.tbb.settings.openfoam.streaming_sequence
    assert seq_settings.name == "My_OpenFOAM_Streaming_Sim_sequence"
    assert seq_settings.update == True
    assert seq_settings.file_path == FILE_PATH
    assert seq_settings.frame_start == 1
    assert seq_settings.max_length == 21
    assert seq_settings.anim_length == 21
    assert seq_settings.import_point_data == True
    assert seq_settings.list_point_data == "U;alpha.water;p;p_rgh"

    # Test OpenFOAM settings
    assert seq_settings.decompose_polyhedra == True
    assert seq_settings.triangulate == True
    assert seq_settings.case_type == 'reconstructed'
    assert seq_settings.clip.type == 'scalar'
    assert seq_settings.clip.scalar.value == 0.5
    assert seq_settings.clip.scalar.name == "alpha.water@value"
    assert seq_settings.clip.scalar.invert == False


def test_geometry_streaming_sequence_openfoam(streaming_sequence):
    assert streaming_sequence is not None

    # Change frame to load another time point for the mesh sequence
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(11)
    # Disable updates for this sequence object during the next tests
    streaming_sequence.tbb.settings.openfoam.streaming_sequence.update = False

    # Test geometry (tp 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    assert len(streaming_sequence.data.vertices) == 55718
    assert len(streaming_sequence.data.edges) == 159953
    assert len(streaming_sequence.data.polygons) == 104450


def test_point_data_streaming_sequence_openfoam(streaming_sequence):
    assert streaming_sequence is not None

    # Test point data (only test if they exist)
    vertex_colors = streaming_sequence.data.vertex_colors
    assert len(vertex_colors) == 2
    u_colors = vertex_colors.get("U.x, U.y, U.z", None)
    assert u_colors is not None
    aw_p_prgh_colors = vertex_colors.get("alpha.water, p, p_rgh", None)
    assert aw_p_prgh_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])


def test_create_mesh_sequence_openfoam(scene_settings):
    # Set clip settings
    scene_settings.clip.type = 'scalar'
    scene_settings.clip.scalar.name = 'alpha.water@value'
    scene_settings.clip.scalar.value = 0.5

    # Set sequence settings
    scene_settings.sequence_type = "mesh_sequence"
    scene_settings["start_time_point"] = 8
    scene_settings["end_time_point"] = 11
    scene_settings.import_point_data = True
    scene_settings.list_point_data = "U;alpha.water;p;p_rgh"
    scene_settings.sequence_name = "My_OpenFOAM_Sim"

    # Change frame to create the mesh sequence from another frame
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(9)
    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}


def test_mesh_sequence_openfoam(mesh_sequence):
    assert mesh_sequence is not None

    # Change frame to load another time point for the mesh sequence
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(11)

    # Test mesh sequence (settings from Stop-Motion-OBJ)
    assert mesh_sequence.mesh_sequence_settings.numMeshes == 4
    assert mesh_sequence.mesh_sequence_settings.numMeshesInMemory == 4
    assert mesh_sequence.mesh_sequence_settings.startFrame == 1
    assert mesh_sequence.mesh_sequence_settings.speed == 1.0
    assert mesh_sequence.mesh_sequence_settings.streamDuringPlayback == True
    assert mesh_sequence.mesh_sequence_settings.showAsSingleMesh == False
    assert mesh_sequence.mesh_sequence_settings.perFrameMaterial == False
    assert mesh_sequence.mesh_sequence_settings.loaded == True
    assert mesh_sequence.mesh_sequence_settings.initialized == True
    assert mesh_sequence.mesh_sequence_settings.name == ""
    assert mesh_sequence.mesh_sequence_settings.meshNames == ""
    assert mesh_sequence.mesh_sequence_settings.meshNameArray is not None
    assert mesh_sequence.mesh_sequence_settings.frameMode == '4'
    assert mesh_sequence.mesh_sequence_settings.isImported == False
    assert mesh_sequence.mesh_sequence_settings.fileName == ""


def test_geometry_mesh_sequence_openfoam(mesh_sequence):
    assert mesh_sequence is not None

    # Test geometry (tp 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    assert len(mesh_sequence.data.vertices) == 55718
    assert len(mesh_sequence.data.edges) == 159953
    assert len(mesh_sequence.data.polygons) == 104450


def test_point_data_mesh_sequence_openfoam(mesh_sequence):
    assert mesh_sequence is not None

    # Test point data (only test if they exist)
    vertex_colors = mesh_sequence.data.vertex_colors
    assert len(vertex_colors) == 2
    u_colors = vertex_colors.get("U.x, U.y, U.z", None)
    assert u_colors is not None
    aw_p_prgh_colors = vertex_colors.get("alpha.water, p, p_rgh", None)
    assert aw_p_prgh_colors is not None

    # TODO: compare values (warning: color data are ramapped into [0; 1])
