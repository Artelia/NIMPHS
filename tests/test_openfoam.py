# <pep8 compliant>
import os
import bpy
import json
import pytest
import pyvista

# Sample A:
# Number of time points = 21

# Non-triangulated mesh: Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092
# Non-triangulated-mesh (decomp. polyh.): Vertices = 60,548 | Edges = 121,748 | Faces = 61,202 | Triangles = 121,092
# Triangulated mesh (w/wo decomp. polyh.): Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092

# Time point 11, clip alpha.water (value = 0.5):
# Vertices = 55,099 | Edges = 158,461 | Faces = 103,540 | Triangles = 103,540

FILE_PATH = os.path.abspath("./data/openfoam_sample_a/foam.foam")


@pytest.fixture
def preview_object():
    obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj


@pytest.fixture
def mesh_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Sim_sequence", None)


@pytest.fixture
def streaming_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)


def test_import_openfoam():
    op = bpy.ops.tbb.import_openfoam_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="here.foam") == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}


def test_preview_object_openfoam(preview_object):
    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092

    # Test object properties
    assert preview_object.tbb.module == 'OpenFOAM'
    assert preview_object.tbb.uid != ""
    assert preview_object.tbb.is_streaming_sequence is False
    assert preview_object.tbb.is_mesh_sequence is False
    # Test object settings
    assert preview_object.tbb.settings.file_path == FILE_PATH


def test_file_data(preview_object):
    assert preview_object is not None

    file_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.module == "OpenFOAM"
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)
    assert isinstance(file_data.mesh, pyvista.PolyData)
    assert file_data.time_point == 0
    assert file_data.nb_time_points == 21
    assert file_data.vars is not None


def test_reload_openfoam(preview_object):
    assert bpy.ops.tbb.reload_openfoam_file('EXEC_DEFAULT') == {"FINISHED"}

    file_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.module == "OpenFOAM"
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)
    assert isinstance(file_data.mesh, pyvista.UnstructuredGrid)
    assert file_data.time_point == 0
    assert file_data.nb_time_points == 21
    assert file_data.vars is not None


def test_normal_preview_object_openfoam(preview_object):
    # Get import settings
    io_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    io_settings.decompose_polyhedra = False
    io_settings.triangulate = False
    io_settings.case_type = 'reconstructed'

    # TODO: test every sort of output this operator can generate
    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_preview_object(preview_object):
    # Test geometry
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.edges) == 120428
    assert len(preview_object.data.polygons) == 59882


def test_normal_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Get import settings
    import_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    import_settings.decompose_polyhedra = True
    import_settings.triangulate = False
    import_settings.case_type = 'reconstructed'

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Test geometry
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.edges) == 121748
    assert len(preview_object.data.polygons) == 61202


def test_triangulated_preview_object_openfoam(preview_object):
    # Get import settings
    import_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    import_settings.decompose_polyhedra = False
    import_settings.triangulate = True
    import_settings.case_type = 'reconstructed'

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_triangulated_preview_object_openfoam(preview_object):
    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092


def test_triangulated_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Get import settings
    import_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    import_settings.decompose_polyhedra = True
    import_settings.triangulate = True
    import_settings.case_type = 'reconstructed'

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_triangulated_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Test geometry
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.polygons) == 121092


def test_add_point_data(preview_object):
    pytest.skip("Not implemented yet")
    tmp_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert tmp_data is not None

    # TODO: Fix this. Not working.
    op = bpy.ops.tbb.add_point_data
    state = op('INVOKE_DEFAULT', available=tmp_data.vars.dumps(),
               chosen=preview_object.tbb.settings.point_data.list, source='OBJECT')
    assert state == {'FINISHED'}

    state = op('EXEC_DEFAULT', available=tmp_data.vars.dumps(),
               chosen=preview_object.tbb.settings.point_data.list, source='OBJECT',
               point_data="None")
    assert state == {'FINISHED'}


def test_remove_point_data(preview_object):
    pytest.skip("Not implemented yet")
    # TODO: First fix add_point_data test. Then complete this one.
    tmp_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert tmp_data is not None


def test_preview_point_data(preview_object):
    tmp_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert tmp_data is not None

    # Set point data to preview (alpha.water)
    preview_object.tbb.settings.preview_point_data = json.dumps(tmp_data.vars.get(1))

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_point_data_preview_object_openfoam(preview_object):
    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    vertex_colors = preview_object.data.vertex_colors
    assert len(vertex_colors) == 1
    data = vertex_colors.get("alpha.water, None, None", None)
    assert data is not None


def test_preview_material_openfoam():
    # Test preview material
    prw_mat = bpy.data.materials.get("TBB_OpenFOAM_preview_material", None)
    assert prw_mat is not None
    assert prw_mat.use_nodes is True
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


def test_create_streaming_sequence_openfoam(preview_object):
    tmp_data = bpy.context.scene.tbb.tmp_data.get(preview_object.tbb.uid, None)
    assert tmp_data is not None

    op = bpy.ops.tbb.openfoam_create_streaming_sequence
    state = op('EXEC_DEFAULT', name="My_OpenFOAM_Streaming_Sim", start=1, length=21, max_length=21, shade_smooth=True)
    assert state == {'FINISHED'}

    # Get sequence
    sequence = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert sequence is not None

    # Set import settings
    sequence.tbb.settings.openfoam.import_settings.case_type = 'reconstructed'
    sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra = True
    sequence.tbb.settings.openfoam.import_settings.triangulate = True
    # Set clip settings
    sequence.tbb.settings.openfoam.clip.type = 'SCALAR'
    sequence.tbb.settings.openfoam.clip.scalar.name = json.dumps(tmp_data.vars.get(1))
    sequence.tbb.settings.openfoam.clip.scalar.value = 0.5
    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = json.dumps(tmp_data.vars.get(1))


def test_streaming_sequence_openfoam(streaming_sequence):
    assert streaming_sequence is not None
    assert streaming_sequence.tbb.is_streaming_sequence is True

    tmp_data = bpy.context.scene.tbb.tmp_data.get(streaming_sequence.tbb.uid, None)
    assert tmp_data is not None

    # Test object settings
    streaming_sequence.tbb.settings.file_path == FILE_PATH

    # Test sequence settings
    sequence = streaming_sequence.tbb.settings.openfoam.s_sequence
    assert sequence.update is True
    # assert sequence.start == 1 # TODO: fix this test.
    assert sequence.max_length == 21
    assert sequence.length == 21

    # Test import settings
    assert streaming_sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra is True
    assert streaming_sequence.tbb.settings.openfoam.import_settings.case_type == 'reconstructed'
    assert streaming_sequence.tbb.settings.openfoam.import_settings.triangulate is True
    # Test clip settings
    assert streaming_sequence.tbb.settings.openfoam.clip.type == 'SCALAR'
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.name == json.dumps(tmp_data.vars.get(1))
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.value == 0.5
    # Test point data
    assert streaming_sequence.tbb.settings.point_data.import_data is True
    assert streaming_sequence.tbb.settings.point_data.list == json.dumps(tmp_data.vars.get(1))


def test_geometry_streaming_sequence_openfoam(streaming_sequence):
    # Change frame to load another time point for the mesh sequence
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(11)
    # Disable updates for this sequence object during the next tests
    streaming_sequence.tbb.settings.openfoam.s_sequence.update = False

    # Test geometry (time point 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    assert len(streaming_sequence.data.vertices) == 55099
    assert len(streaming_sequence.data.edges) == 158461
    assert len(streaming_sequence.data.polygons) == 103540


def test_point_data_streaming_sequence_openfoam(streaming_sequence):
    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    vertex_colors = streaming_sequence.data.vertex_colors
    assert len(vertex_colors) == 1
    data = vertex_colors.get("alpha.water, None, None", None)
    assert data is not None


def test_create_mesh_sequence_openfoam():
    # Change frame to create the mesh sequence from another frame
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(9)
    op = bpy.ops.tbb.openfoam_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=21, end=4, name="My_OpenFOAM_Sim", mode='NORMAL')
    assert state == {"FINISHED"}


def test_mesh_sequence_openfoam(mesh_sequence):
    assert mesh_sequence is not None

    # Change frame to load another time point for the mesh sequence
    # WARNING: next tests are based on the following frame
    bpy.context.scene.frame_set(11)

    # Test mesh sequence (settings from Stop-Motion-OBJ)
    assert mesh_sequence.mesh_sequence_settings.numMeshes == 5
    assert mesh_sequence.mesh_sequence_settings.numMeshesInMemory == 5
    assert mesh_sequence.mesh_sequence_settings.startFrame == 1
    assert mesh_sequence.mesh_sequence_settings.speed == 1.0
    assert mesh_sequence.mesh_sequence_settings.streamDuringPlayback is True
    assert mesh_sequence.mesh_sequence_settings.perFrameMaterial is False
    assert mesh_sequence.mesh_sequence_settings.loaded is True
    assert mesh_sequence.mesh_sequence_settings.initialized is True
    assert mesh_sequence.mesh_sequence_settings.name == ""
    assert mesh_sequence.mesh_sequence_settings.meshNames == ""
    assert mesh_sequence.mesh_sequence_settings.meshNameArray is not None
    assert mesh_sequence.mesh_sequence_settings.frameMode == '4'
    assert mesh_sequence.mesh_sequence_settings.isImported is False
    assert mesh_sequence.mesh_sequence_settings.fileName == ""


def test_geometry_mesh_sequence_openfoam(mesh_sequence):
    assert mesh_sequence is not None

    # Test geometry
    assert len(mesh_sequence.data.vertices) == 61616
    assert len(mesh_sequence.data.edges) == 182698
    assert len(mesh_sequence.data.polygons) == 121092


def test_point_data_mesh_sequence_openfoam(mesh_sequence):
    pytest.skip("Not implemented yet")
    assert mesh_sequence is not None

    # Test point data (only test if they exist)
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    # TODO: fix 'test generate mesh sequence' to do this test (add point data)
    vertex_colors = mesh_sequence.data.vertex_colors
    assert len(vertex_colors) == 1
    data = vertex_colors.get("alpha.water, None, None", None)
    assert data is not None
