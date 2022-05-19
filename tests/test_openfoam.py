import os
import bpy

# Sample A:
# Number of time points = 21
# Non-triangulated mesh: Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092
# Non-triangulated-mesh (decomp. polyh.): Vertices = 60,548 | Edges = 121,748 | Faces = 61,202 | Triangles = 121,092
# Triangulated mesh (w/wo decomp. polyh.): Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092
# Time point 11, clip aplha.water (value = 0.5):
# Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092

FILE_PATH = os.path.abspath("./data/openfoam_sample_a/foam.foam")


def test_import_openfoam():
    assert bpy.ops.tbb.import_openfoam_file('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}

    tmp_data = bpy.context.scene.tbb.settings.openfoam.tmp_data

    # Test temporary data default parameters
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21

    # Test preview object
    prw_obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    assert prw_obj is not None
    # Test geometry
    assert len(prw_obj.data.vertices) == 61616
    assert len(prw_obj.data.edges) == 182698
    assert len(prw_obj.data.polygons) == 121092


def test_reload_openfoam():
    assert bpy.ops.tbb.reload_openfoam_file('EXEC_DEFAULT') == {"FINISHED"}

    # Test temporary data parameters
    tmp_data = bpy.context.scene.tbb.settings.openfoam.tmp_data
    assert tmp_data.time_point == 0
    assert tmp_data.module_name == "OpenFOAM"
    assert tmp_data.file_reader is not None
    assert tmp_data.data is not None
    assert tmp_data.mesh is not None
    assert tmp_data.nb_time_points == 21


def test_normal_preview_object_openfoam():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = False
    settings.triangulate = False

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}

    prw_obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    assert prw_obj is not None
    # Test geometry
    assert len(prw_obj.data.vertices) == 60548
    assert len(prw_obj.data.edges) == 120428
    assert len(prw_obj.data.polygons) == 59882


def test_normal_decompose_polyhedra_preview_object_openfoam():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = True
    settings.triangulate = False

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}

    prw_obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    assert prw_obj is not None
    # Test geometry
    assert len(prw_obj.data.vertices) == 60548
    assert len(prw_obj.data.edges) == 121748
    assert len(prw_obj.data.polygons) == 61202


def test_triangulated_preview_object_openfoam():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = False
    settings.triangulate = True

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}

    prw_obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    assert prw_obj is not None
    # Test geometry
    assert len(prw_obj.data.vertices) == 61616
    assert len(prw_obj.data.edges) == 182698
    assert len(prw_obj.data.polygons) == 121092


def test_triangulated_decompose_polyhedra_preview_object_openfoam():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = True
    settings.triangulate = True

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}

    prw_obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    assert prw_obj is not None
    # Test geometry
    assert len(prw_obj.data.vertices) == 61616
    assert len(prw_obj.data.edges) == 182698
    assert len(prw_obj.data.polygons) == 121092


def test_preview_material_openfoam():
    # Set preview settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = True
    settings.triangulate = True
    settings.preview_point_data = "alpha.water@value"

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}

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


def test_create_streaming_sequence_openfoam():
    # Set file settings
    settings = bpy.context.scene.tbb.settings.openfoam
    settings.decompose_polyhedra = True
    settings.triangulate = True

    # Set clip settings
    settings.clip.type = 'scalar'
    settings.clip.scalar.name = 'alpha.water@value'
    settings.clip.scalar.value = 0.5

    # Set sequence settings
    settings.sequence_type = "streaming_sequence"
    settings.frame_start = 1
    settings["anim_length"] = 21
    settings.import_point_data = True
    settings.list_point_data = "U;alpha.water;p;p_rgh"
    settings.sequence_name = "My_OpenFOAM_Streaming_Sim"

    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT') == {"FINISHED"}

    # Test created sequence settings
    seq_obj = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert seq_obj is not None
    assert seq_obj.tbb.is_streaming_sequence == True

    # Test common settings
    seq_settings = seq_obj.tbb.settings.openfoam.streaming_sequence
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
    assert seq_settings.clip.type == 'scalar'
    assert seq_settings.clip.scalar.value == 0.5
    assert seq_settings.clip.scalar.name == "alpha.water@value"
    assert seq_settings.clip.scalar.invert == False


def test_streaming_sequence_openfoam():
    seq_obj = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert seq_obj is not None

    # Change frame to load another time point for the streaming sequence
    bpy.context.scene.frame_set(10)

    # Test geometry


def test_create_mesh_sequence_openfoam():
    settings = bpy.context.scene.tbb.settings.openfoam
    assert settings is not None

    # Set clip settings
    settings.clip.type = 'scalar'
    settings.clip.scalar.name = 'alpha.water@value'
    settings.clip.scalar.value = 0.5

    # Set sequence settings
    settings.sequence_type = "mesh_sequence"
    settings["start_time_point"] = 0
    settings["end_time_point"] = 5
    settings.import_point_data = True
    settings.list_point_data = "U;alpha.water;p;p_rgh"
    settings.sequence_name = "My_OpenFOAM_Sim"

    assert bpy.ops.tbb.openfoam_create_sequence('EXEC_DEFAULT', mode='NORMAL') == {"FINISHED"}

    # TODO: Test geometry and impoted point data
