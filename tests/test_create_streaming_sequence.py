# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import warnings

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_create_streaming_sequence_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 11
    bpy.context.scene.frame_set(11)

    # Set test data
    data = json.dumps({"start": 1, "length": 20})

    op = bpy.ops.tbb.openfoam_create_streaming_sequence
    state = op('EXEC_DEFAULT', name=utils.STREAMING_SEQUENCE_OBJ_NAME, shade_smooth=True, test_data=data)
    assert state == {'FINISHED'}

    # Get and check sequence
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    assert obj is not None
    assert obj.tbb.is_streaming_sequence is True

    # Set import settings
    obj.tbb.settings.openfoam.import_settings.triangulate = True
    obj.tbb.settings.openfoam.import_settings.skip_zero_time = True
    obj.tbb.settings.openfoam.import_settings.decompose_polyhedra = True
    obj.tbb.settings.openfoam.import_settings.case_type = 'reconstructed'

    # Set clip settings
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    obj.tbb.settings.openfoam.clip.type = 'SCALAR'
    obj.tbb.settings.openfoam.clip.scalar.value = 0.5
    obj.tbb.settings.openfoam.clip.scalar.name = json.dumps(file_data.vars.get("alpha.water"))

    # Set point data
    obj.tbb.settings.point_data.import_data = True
    obj.tbb.settings.point_data.list = utils.get_point_data_openfoam(True).dumps()


def test_streaming_sequence_openfoam():
    # Force update streaming sequence
    handler = utils.get_frame_change_pre_app_handler("update_openfoam_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)

    # Test object settings
    obj.tbb.settings.file_path == utils.FILE_PATH_OPENFOAM

    # Test sequence settings
    assert obj.tbb.settings.openfoam.s_sequence.max == 20
    assert obj.tbb.settings.openfoam.s_sequence.start == 1
    assert obj.tbb.settings.openfoam.s_sequence.length == 20
    assert obj.tbb.settings.openfoam.s_sequence.update is True

    # Test import settings
    assert obj.tbb.settings.openfoam.import_settings.triangulate is True
    assert obj.tbb.settings.openfoam.import_settings.skip_zero_time is True
    assert obj.tbb.settings.openfoam.import_settings.decompose_polyhedra is True
    assert obj.tbb.settings.openfoam.import_settings.case_type == 'reconstructed'

    # Test clip settings
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    assert obj.tbb.settings.openfoam.clip.type == 'SCALAR'
    assert obj.tbb.settings.openfoam.clip.scalar.value == 0.5
    assert obj.tbb.settings.openfoam.clip.scalar.name == json.dumps(file_data.vars.get("alpha.water"))


def test_geometry_streaming_sequence_openfoam():
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)

    # Test geometry (time point 11, clip on alpha.water, 0.5, triangulated, decompose polyhedra)
    mesh = sample["mesh"]["clipped"]["mesh"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.polygons) == mesh["faces"]
    assert len(obj.data.vertices) == mesh["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_streaming_sequence_openfoam():
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["variables"]["skip_zero_true"]

    # Remove clip settings to test point data values
    obj.tbb.settings.openfoam.clip.type = 'NONE'

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 2
    bpy.context.scene.frame_set(3)

    # Check number of vertex color layers
    assert len(obj.data.vertex_colors) == 5

    # Test point data values
    for i in range(len(obj.data.vertex_colors)):
        for name, channel in zip(obj.data.vertex_colors[i].name.split(', '), range(3)):
            data = obj.data.vertex_colors[i]
            try:
                ground_truth = vars[name]["mean"]
                subtraction = abs(utils.compute_mean_value(data, obj, channel) - ground_truth)
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


def test_create_streaming_sequence_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()

    # Set test data
    data = json.dumps({"start": 1, "length": 11})

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', name=utils.STREAMING_SEQUENCE_OBJ_NAME, module='TELEMAC',
               shade_smooth=True, test_data=data)
    assert state == {'FINISHED'}

    # Get and check sequence object
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    assert obj is not None
    assert len(obj.children) == 2

    # Set point data
    obj.tbb.settings.point_data.import_data = True
    obj.tbb.settings.point_data.list = utils.get_point_data_telemac('2D').dumps()


def test_streaming_sequence_telemac_2d():
    # Force update streaming sequence
    handler = utils.get_frame_change_pre_app_handler("update_telemac_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)

    # Test object settings
    assert obj.tbb.uid != ""
    assert obj.tbb.module == 'TELEMAC'
    assert obj.tbb.is_mesh_sequence is False
    assert obj.tbb.is_streaming_sequence is True
    assert obj.tbb.settings.file_path == utils.FILE_PATH_TELEMAC_2D

    # Test streaming sequence settings
    assert obj.tbb.settings.telemac.s_sequence.max == 11
    assert obj.tbb.settings.telemac.s_sequence.start == 1
    assert obj.tbb.settings.telemac.s_sequence.length == 11
    assert obj.tbb.settings.telemac.s_sequence.update is True


def test_geometry_streaming_sequence_telemac_2d():
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    # Test geometry
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.polygons) == sample["mesh"]["faces"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_streaming_sequence_telemac_2d():
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(6)

    # Test point data values
    for child in obj.children:
        # Check number vertex colors arrays
        data = child.data.vertex_colors
        assert len(data) == 2

        for i in range(len(data)):
            for name, channel in zip(data[i].name.split(", "), range(3)):
                if name != 'None':
                    ground_truth = sample["variables"][name]["mean"]
                    subtraction = abs(utils.compute_mean_value(data[i], child, channel) - ground_truth)
                    utils.compare_point_data_value(subtraction, name)


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_create_streaming_sequence_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Select preview object
    obj = utils.get_preview_object()

    # Set test data
    data = json.dumps({"start": 1, "length": 11})

    op = bpy.ops.tbb.telemac_create_streaming_sequence
    state = op('EXEC_DEFAULT', name=utils.STREAMING_SEQUENCE_OBJ_NAME, module='TELEMAC',
               shade_smooth=True, test_data=data)
    assert state == {'FINISHED'}

    # Get and check sequence object
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    assert obj is not None
    assert len(obj.children) == 3

    # Set point data
    obj.tbb.settings.point_data.import_data = True
    obj.tbb.settings.point_data.list = utils.get_point_data_telemac('3D').dumps()


def test_streaming_sequence_telemac_3d():
    # Force update streaming sequence
    handler = utils.get_frame_change_pre_app_handler("update_telemac_streaming_sequences")
    assert handler is not None
    handler(bpy.context.scene)

    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)

    # Test object settings
    assert obj.tbb.uid != ""
    assert obj.tbb.module == 'TELEMAC'
    assert obj.tbb.is_mesh_sequence is False
    assert obj.tbb.is_streaming_sequence is True
    assert obj.tbb.settings.file_path == utils.FILE_PATH_TELEMAC_3D

    # Test streaming sequence settings
    assert obj.tbb.settings.telemac.s_sequence.max == 11
    assert obj.tbb.settings.telemac.s_sequence.start == 1
    assert obj.tbb.settings.telemac.s_sequence.length == 11
    assert obj.tbb.settings.telemac.s_sequence.update is True


def test_geometry_streaming_sequence_telemac_3d():
    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Test geometry
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.polygons) == sample["mesh"]["faces"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_streaming_sequence_telemac_3d():
    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 5
    bpy.context.scene.frame_set(6)

    obj = bpy.data.objects.get(utils.STREAMING_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # Initialize SPMV (Sum partial mean values)
    spmv = {}
    for name in sample["VariablesInformation"]["names"]:
        spmv[name] = 0.0

    # Test point data values
    for child in obj.children:
        # Check number vertex colors arrays
        data = child.data.vertex_colors
        assert len(data) == 2

        for i in range(len(data)):
            for name, channel in zip(data[i].name.split(", "), range(3)):
                if name != 'None':
                    spmv[name] += utils.compute_mean_value(data[i], child, channel)

    # Compare values
    for name in sample["VariablesInformation"]["names"]:
        subtraction = abs(spmv[name] - sample["variables"][name]["spmv"])
        utils.compare_point_data_value(subtraction, name)
