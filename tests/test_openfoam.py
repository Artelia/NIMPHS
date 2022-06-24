# <pep8 compliant>
import os
import bpy
import json
import pytest
import pyvista
import numpy as np

# Sample A:
#   If not skip_zero_time:
#                       (Time point = 11)               (GLOBAL)                        (GLOBAL)
#       U[0]:           mean = 0.4982270006854066       min = -1.346832513809204        max = 1.345022439956665
#       U[1]:           mean = 1.0                      min = -4.208540108459135e-17    max = 9.689870304643004e-17
#       U[2]:           mean = 0.6844272828995177       min = -4.320412635803223        max = 1.1953175067901611
#       alpha.water:    mean = 0.8128361873018102       min = 0.0                       max = 1.0
#       nut:            mean = 0.28475841868228513      min = 0.0                       max = 0.006597405299544334
#
#       Number of time points = 21
#       Number of variables = 3

#   If skip_zero_time:
#       U:              min =
#       alpha.water:    min =
#       nut:            min =
#
#       Number of time points = ?
#       Number of variables = ?

#   Non-triangulated mesh:
#       Vertices = 60,548 | Edges = 120,428 | Faces = 59,882 | Triangles = 121,092

#   Non-triangulated-mesh (decomp. polyh.):
#       Vertices = 60,548 | Edges = 121,748 | Faces = 61,202 | Triangles = 121,092

#   Triangulated mesh (w/wo decomp. polyh.):
#       Vertices = 61,616 | Edges = 182,698 | Faces = 121,092 | Triangles = 121,092

#   Time point 11, clip alpha.water (value = 0.5):
#       Vertices = 55,099 | Edges = 158,461 | Faces = 103,540 | Triangles = 103,540

FILE_PATH = os.path.abspath("./data/openfoam_sample_a/foam.foam")
# Point data value threshold for tests
PDV_THRESHOLD = 0.008


@pytest.fixture
def mesh_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Sim_sequence", None)


@pytest.fixture
def streaming_sequence():
    return bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)


@pytest.fixture
def preview_object():
    obj = bpy.data.objects.get("TBB_OpenFOAM_preview", None)
    # If not None, select the object
    if obj is not None:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    return obj


@pytest.fixture
def point_data_test_a():
    from tbb.properties.utils import VariablesInformation

    data = VariablesInformation()
    data.append(name="U", type="VECTOR", dim=3)
    data.append(name="alpha.water", type="SCALAR")
    data.append(name="nut", type="SCALAR")

    return data


@pytest.fixture
def get_mean_value():
    from bpy.types import Object, MeshLoopColorLayer

    def mean_value(colors: MeshLoopColorLayer, obj: Object, channel: int):
        data = [0] * len(obj.data.loops) * 4
        colors.data.foreach_get("color", data)
        extracted = [data[i] for i in range(channel, len(data), 4)]
        return np.sum(extracted) / len(obj.data.loops)

    return mean_value


@pytest.fixture
def frame_change_pre():

    def get_handler(name: str):
        for handler in bpy.app.handlers.frame_change_pre:
            if handler.__name__ == name:
                return handler

        return None

    return get_handler


def test_import_openfoam():
    op = bpy.ops.tbb.import_openfoam_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="here.foam") == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=FILE_PATH) == {"FINISHED"}


def test_imported_object_openfoam(preview_object):
    # Check imported object
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.polygons) == 121092

    # Test object properties
    assert preview_object.tbb.uid != ""
    assert preview_object.tbb.module == 'OpenFOAM'
    assert preview_object.tbb.is_mesh_sequence is False
    assert preview_object.tbb.is_streaming_sequence is False

    # Test object settings
    assert preview_object.tbb.settings.file_path == FILE_PATH


def test_file_data_imported_object_openfoam(preview_object):
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.time_point == 0
    assert file_data.vars is not None
    assert file_data.module == "OpenFOAM"
    assert file_data.nb_time_points == 21
    assert isinstance(file_data.mesh, pyvista.PolyData)
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)


def test_reload_file_data_openfoam(preview_object):
    assert bpy.ops.tbb.reload_openfoam_file('EXEC_DEFAULT') == {"FINISHED"}

    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.time_point == 0
    assert file_data.vars is not None
    assert file_data.module == "OpenFOAM"
    assert file_data.nb_time_points == 21
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.mesh, pyvista.UnstructuredGrid)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)


def test_normal_preview_object_openfoam(preview_object):
    # Get import settings
    io_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    io_settings.triangulate = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = False

    # TODO: test every sort of output this operator can generate
    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_preview_object(preview_object):
    # Check preview object
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.edges) == 120428
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.polygons) == 59882


def test_normal_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Get import settings
    import_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    import_settings.triangulate = False
    import_settings.case_type = 'reconstructed'
    import_settings.decompose_polyhedra = True

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_normal_decompose_polyhedra_preview_object_openfoam(preview_object):
    # Check preview object
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.edges) == 121748
    assert len(preview_object.data.vertices) == 60548
    assert len(preview_object.data.polygons) == 61202


def test_triangulated_preview_object_openfoam(preview_object):
    # Get import settings
    import_settings = preview_object.tbb.settings.openfoam.import_settings

    # Set preview settings
    import_settings.triangulate = True
    import_settings.case_type = 'reconstructed'
    import_settings.decompose_polyhedra = False

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_geometry_triangulated_preview_object_openfoam(preview_object):
    # Check preview object
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.vertices) == 61616
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
    # Check preview object
    assert preview_object is not None

    # Test geometry
    assert len(preview_object.data.edges) == 182698
    assert len(preview_object.data.vertices) == 61616
    assert len(preview_object.data.polygons) == 121092


def test_add_point_data_openfoam(preview_object):
    pytest.skip("Not implemented yet")
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # TODO: Fix this. Not working.
    op = bpy.ops.tbb.add_point_data
    state = op('INVOKE_DEFAULT', available=file_data.vars.dumps(),
               chosen=preview_object.tbb.settings.point_data.list, source='OBJECT')
    assert state == {'FINISHED'}

    state = op('EXEC_DEFAULT', available=file_data.vars.dumps(),
               chosen=preview_object.tbb.settings.point_data.list, source='OBJECT',
               point_data="None")
    assert state == {'FINISHED'}


def test_remove_point_data_openfoam(preview_object):
    pytest.skip("Not implemented yet")
    # TODO: First fix add_point_data test. Then complete this one.
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None


def test_preview_point_data(preview_object, point_data_test_a):
    # Set point data to preview
    preview_object.tbb.settings.preview_time_point = 11
    preview_object.tbb.settings.preview_point_data = json.dumps(point_data_test_a.get("alpha.water"))

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {"FINISHED"}


def test_point_data_preview_object_openfoam(preview_object, get_mean_value):
    # Check preview object
    assert preview_object is not None

    # Check number vertex colors arrays
    vertex_colors = preview_object.data.vertex_colors
    assert len(vertex_colors) == 1

    # Test point data values
    data = vertex_colors.get("alpha.water, None, None", None)
    assert data is not None

    assert np.abs(get_mean_value(data, preview_object, 0) - 0.8128361873018102) < PDV_THRESHOLD


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


def test_compute_ranges_point_data_values_openfoam(preview_object, point_data_test_a):
    op = bpy.ops.tbb.compute_ranges_point_data_values
    assert op('EXEC_DEFAULT', mode='TEST', test_data=point_data_test_a.dumps()) == {'FINISHED'}

    # Check file data
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    # Test computed values
    alpha_water = file_data.vars.get("alpha.water", prop='RANGE')["global"]
    assert alpha_water["min"] == 0.0 and alpha_water["max"] == 1.0

    nut = file_data.vars.get("nut", prop='RANGE')["global"]
    assert nut["min"] == 0.0 and nut["max"] == 0.006597405299544334

    u = file_data.vars.get("U", prop='RANGE')["global"]
    assert u["min"][0] == -1.346832513809204
    assert u["min"][1] == -4.208540108459135e-17
    assert u["min"][2] == -4.320412635803223
    assert u["max"][0] == 1.345022439956665
    assert u["max"][1] == 9.689870304643004e-17
    assert u["max"][2] == 1.1953175067901611


def test_create_streaming_sequence_openfoam(preview_object, point_data_test_a):
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 11
    bpy.context.scene.frame_set(11)

    op = bpy.ops.tbb.openfoam_create_streaming_sequence
    state = op('EXEC_DEFAULT', name="My_OpenFOAM_Streaming_Sim", start=1, length=21, max_length=21, shade_smooth=True)
    assert state == {'FINISHED'}

    # Get and check sequence
    sequence = bpy.data.objects.get("My_OpenFOAM_Streaming_Sim_sequence", None)
    assert sequence is not None
    assert sequence.tbb.is_streaming_sequence is True

    # Set import settings
    sequence.tbb.settings.openfoam.import_settings.triangulate = True
    sequence.tbb.settings.openfoam.import_settings.case_type = 'reconstructed'
    sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra = True

    # Set clip settings
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None

    sequence.tbb.settings.openfoam.clip.type = 'SCALAR'
    sequence.tbb.settings.openfoam.clip.scalar.value = 0.5
    sequence.tbb.settings.openfoam.clip.scalar.name = json.dumps(file_data.vars.get("alpha.water"))

    # Set point data
    sequence.tbb.settings.point_data.import_data = True
    sequence.tbb.settings.point_data.list = point_data_test_a.dumps()


def test_streaming_sequence_openfoam(streaming_sequence, frame_change_pre):
    # Force update streaming sequences
    handler = frame_change_pre("update_openfoam_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Disable updates for this sequence object during the next tests
    streaming_sequence.tbb.settings.openfoam.s_sequence.update = False

    # Test object settings
    streaming_sequence.tbb.settings.file_path == FILE_PATH

    # Test sequence settings
    sequence = streaming_sequence.tbb.settings.openfoam.s_sequence
    # assert sequence.start == 1 # TODO: fix this test.
    assert sequence.length == 21
    assert sequence.update is False
    assert sequence.max_length == 21

    # Test import settings
    assert streaming_sequence.tbb.settings.openfoam.import_settings.triangulate is True
    assert streaming_sequence.tbb.settings.openfoam.import_settings.case_type == 'reconstructed'
    assert streaming_sequence.tbb.settings.openfoam.import_settings.decompose_polyhedra is True

    # Test clip settings
    file_data = bpy.context.scene.tbb.file_data.get(streaming_sequence.tbb.uid, None)
    assert file_data is not None

    assert streaming_sequence.tbb.settings.openfoam.clip.type == 'SCALAR'
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.value == 0.5
    assert streaming_sequence.tbb.settings.openfoam.clip.scalar.name == json.dumps(file_data.vars.get("alpha.water"))


def test_geometry_streaming_sequence_openfoam(streaming_sequence):
    # Test geometry (time point 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    assert len(streaming_sequence.data.edges) == 158461
    assert len(streaming_sequence.data.vertices) == 55099
    assert len(streaming_sequence.data.polygons) == 103540


def test_point_data_streaming_sequence_openfoam(streaming_sequence):
    # Check number vertex colors arrays
    vertex_colors = streaming_sequence.data.vertex_colors
    assert len(vertex_colors) == 2

    # Test point data values
    # TODO: compare values (warning: color data are ramapped into [0; 1])
    data = vertex_colors.get("U.x, U.y, U.z", None)
    assert data is not None

    data = vertex_colors.get("alpha.water, nut, None", None)
    assert data is not None


def test_create_mesh_sequence_openfoam():
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 9
    bpy.context.scene.frame_set(9)

    op = bpy.ops.tbb.openfoam_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=0, max_length=21, end=4, name="My_OpenFOAM_Sim", mode='TEST')
    assert state == {"FINISHED"}


def test_mesh_sequence_openfoam(mesh_sequence):
    # Checl sequence object
    assert mesh_sequence is not None

    # Test mesh sequence (settings from Stop-Motion-OBJ)
    assert mesh_sequence.mesh_sequence_settings.name == ""
    assert mesh_sequence.mesh_sequence_settings.speed == 1.0
    assert mesh_sequence.mesh_sequence_settings.fileName == ""
    assert mesh_sequence.mesh_sequence_settings.numMeshes == 5
    assert mesh_sequence.mesh_sequence_settings.loaded is True
    assert mesh_sequence.mesh_sequence_settings.meshNames == ""
    assert mesh_sequence.mesh_sequence_settings.startFrame == 1
    assert mesh_sequence.mesh_sequence_settings.frameMode == '4'
    assert mesh_sequence.mesh_sequence_settings.initialized is True
    assert mesh_sequence.mesh_sequence_settings.isImported is False
    assert mesh_sequence.mesh_sequence_settings.numMeshesInMemory == 5
    assert mesh_sequence.mesh_sequence_settings.meshNameArray is not None
    assert mesh_sequence.mesh_sequence_settings.perFrameMaterial is False
    assert mesh_sequence.mesh_sequence_settings.streamDuringPlayback is True


def test_geometry_mesh_sequence_openfoam(mesh_sequence):
    # Test geometry
    assert len(mesh_sequence.data.edges) == 182698
    assert len(mesh_sequence.data.vertices) == 61616
    assert len(mesh_sequence.data.polygons) == 121092


def test_point_data_mesh_sequence_openfoam(mesh_sequence):
    pytest.skip("Not implemented yet")

    # TODO: compare values (warning: color data are ramapped into [0; 1])
    # TODO: fix 'test generate mesh sequence' to do this test (add point data)
    # Check number vertex colors arrays
    vertex_colors = mesh_sequence.data.vertex_colors
    assert len(vertex_colors) == 1

    # Test point data values
    data = vertex_colors.get("alpha.water, None, None", None)
    assert data is not None
