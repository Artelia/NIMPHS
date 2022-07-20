# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_create_mesh_sequence_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', mode='TEST', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["values"]["skip_zero_true"]

    # Get test data (WARNING: this operator changes the current frame)
    data = json.dumps({"vars": utils.get_point_data_openfoam(True).dumps(), "start": 1, "end": vars["time_point"] + 1})

    op = bpy.ops.tbb.openfoam_create_mesh_sequence
    assert op('EXEC_DEFAULT', mode='TEST', name=utils.MESH_SEQUENCE_OBJ_NAME, test_data=data) == {'FINISHED'}

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load test time point
    bpy.context.scene.frame_set(vars["time_point"])


def test_mesh_sequence_openfoam():
    # Check sequence object
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    assert obj is not None

    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["values"]["skip_zero_true"]

    # Test mesh sequence (settings from Stop-Motion-OBJ)
    assert obj.mesh_sequence_settings.name == ""
    assert obj.mesh_sequence_settings.speed == 1.0
    assert obj.mesh_sequence_settings.fileName == ""
    assert obj.mesh_sequence_settings.startFrame == 1
    assert obj.mesh_sequence_settings.loaded is True
    assert obj.mesh_sequence_settings.meshNames == ""
    assert obj.mesh_sequence_settings.frameMode == '4'
    assert obj.mesh_sequence_settings.initialized is True
    assert obj.mesh_sequence_settings.isImported is False
    assert obj.mesh_sequence_settings.meshNameArray is not None
    assert obj.mesh_sequence_settings.perFrameMaterial is False
    assert obj.mesh_sequence_settings.streamDuringPlayback is True
    assert obj.mesh_sequence_settings.numMeshes == vars["time_point"] + 1
    assert obj.mesh_sequence_settings.numMeshesInMemory == vars["time_point"] + 1


def test_geometry_mesh_sequence_openfoam():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)

    # Test geometry
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.polygons) == mesh["faces"]
    assert len(obj.data.vertices) == mesh["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_mesh_sequence_openfoam():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["values"]["skip_zero_true"]

    # Check number of vertex color layers
    assert len(obj.data.vertex_colors) == 5

    # Test point data values
    for i in range(len(obj.data.vertex_colors)):

        data = obj.data.vertex_colors[i]

        for name, channel in zip(obj.data.vertex_colors[i].name.split(', '), range(3)):
            try:
                ground_truth = vars[name]["mean"]
                subtraction = abs(utils.compute_mean_value(data, obj, channel) - ground_truth)
                print(name, utils.compute_mean_value(data, obj, channel), ground_truth)
                utils.compare_point_data_value(subtraction, name)

            except KeyError:
                # Known bug. Can't check point data value because the name of the vertex color
                # name attribute is not big enough to contain these names:
                # - "interfaceCentre.water.x, interfaceCentre.water.y, interfaceCentre.water.z"
                # - "interfaceNormal.water.x, interfaceNormal.water.y, interfaceNormal.water.z"
                if name in ['interfaceCent', 'interfaceNorm']:
                    pass
                else:
                    raise KeyError(f"Key '{name}' not found.")


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_create_mesh_sequence_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    vars = sample["values"]

    # Get test data
    data = json.dumps({"vars": utils.get_point_data_telemac('2D').dumps(), "start": 1, "end": vars["time_point"] + 1})

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to start mesh sequence at frame n°1
    bpy.context.scene.frame_set(1)

    op = bpy.ops.tbb.telemac_create_mesh_sequence
    assert op('EXEC_DEFAULT', name=utils.MESH_SEQUENCE_OBJ_NAME, mode='TEST', test_data=data) == {'FINISHED'}


def test_mesh_sequence_telemac_2d():
    # Check sequence object
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    assert obj is not None
    assert len(obj.children) == 2

    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    vars = sample["values"]

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data[obj.tbb.uid]
    assert file_data is not None

    # Add point data settings
    obj.tbb.settings.point_data.import_data = True
    obj.tbb.settings.point_data.list = utils.get_point_data_telemac('2D').dumps()

    # Force update telemac mesh sequences
    handler = utils.get_frame_change_post_app_handler("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert obj.tbb.uid != ""
    assert obj.tbb.module == 'TELEMAC'
    assert obj.tbb.is_mesh_sequence is True
    assert obj.tbb.is_streaming_sequence is False
    assert obj.tbb.settings.file_path == utils.FILE_PATH_TELEMAC_2D

    # Test sequence data (shape_keys)
    for child in obj.children:
        assert len(child.data.shape_keys.key_blocks) == vars["time_point"]


def test_geometry_mesh_sequence_telemac_2d():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    # Test geometry
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.polygons) == sample["mesh"]["faces"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_mesh_sequence_telemac_2d():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load test time point
    bpy.context.scene.frame_set(sample["values"]["time_point"])

    # Test point data values
    for child in obj.children:
        # Check number vertex colors arrays
        data = child.data.vertex_colors
        assert len(data) == 2

        for i in range(len(data)):
            for name, channel in zip(data[i].name.split(", "), range(3)):
                if name != 'None':
                    ground_truth = sample["values"][name]["mean"]
                    subtraction = abs(utils.compute_mean_value(data[i], child, channel) - ground_truth)
                    utils.compare_point_data_value(subtraction, name)


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_create_mesh_sequence_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()  # noqa: F841
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)
    vars = sample["values"]

    # Get test data
    data = json.dumps({"vars": utils.get_point_data_telemac('3D').dumps(), "start": 1, "end": vars["time_point"] + 1})

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to start mesh sequence at frame n°1
    bpy.context.scene.frame_set(1)

    op = bpy.ops.tbb.telemac_create_mesh_sequence
    assert op('EXEC_DEFAULT', name=utils.MESH_SEQUENCE_OBJ_NAME, mode='TEST', test_data=data) == {'FINISHED'}


def test_mesh_sequence_telemac_3d():
    # Check sequence object
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)
    vars = sample["values"]
    assert obj is not None
    assert len(obj.children) == sample["nb_planes"]

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data[obj.tbb.uid]
    assert file_data is not None

    # Add point data settings
    obj.tbb.settings.point_data.import_data = True
    obj.tbb.settings.point_data.list = utils.get_point_data_telemac('3D').dumps()

    # Force update telemac mesh sequences
    handler = utils.get_frame_change_post_app_handler("update_telemac_mesh_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    # Test object settings
    assert obj.tbb.uid != ""
    assert obj.tbb.module == 'TELEMAC'
    assert obj.tbb.is_mesh_sequence is True
    assert obj.tbb.is_streaming_sequence is False
    assert obj.tbb.settings.file_path == utils.FILE_PATH_TELEMAC_3D

    # Test sequence data (shape_keys)
    for child in obj.children:
        assert len(child.data.shape_keys.key_blocks) == vars["time_point"]


def test_geometry_mesh_sequence_telemac_3d():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Test geometry
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.polygons) == sample["mesh"]["faces"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_mesh_sequence_telemac_3d():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME, None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load test time point
    bpy.context.scene.frame_set(sample["values"]["time_point"])

    # Initialize SPMV (Sum partial mean values)
    spmv = {}
    for name in sample["point_data"]["names"]:
        spmv[name] = 0.0

    # Compute SPMVs
    for child in obj.children:
        # Check number vertex colors arrays
        data = child.data.vertex_colors
        assert len(data) == 2

        for i in range(len(data)):
            for name, channel in zip(data[i].name.split(", "), range(3)):
                if name != 'None':
                    spmv[name] += utils.compute_mean_value(data[i], child, channel)

    # Compare values
    for name in sample["point_data"]["names"]:
        subtraction = abs(spmv[name] - sample["values"][name]["spmv"])
        utils.compare_point_data_value(subtraction, name)
