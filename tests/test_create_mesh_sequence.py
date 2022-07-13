# <pep8 compliant>
import os
import sys
import bpy
import pytest
import pyvista

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects, get_sample_data


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_create_mesh_sequence_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME)  == {'FINISHED'}
    
    # Select preview object
    obj = utils.get_preview_object()

    # ------------------------------------------------------------ #
    # /!\ WARNING: next tests are based on the following frame /!\ #
    # ------------------------------------------------------------ #
    # Change frame to load time point 2
    bpy.context.scene.frame_set(2)

    # Get test data
    data = utils.get_point_data_openfoam(True).dumps()

    op = bpy.ops.tbb.openfoam_create_mesh_sequence
    state = op('EXEC_DEFAULT', start=1, max=21, end=4, name=utils.MESH_SEQUENCE_OBJ_NAME, mode='TEST', test_data=data)
    assert state == {'FINISHED'}


def test_mesh_sequence_openfoam():
    # Check sequence object
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME + "_sequence", None)
    assert obj is not None

    # Test mesh sequence (settings from Stop-Motion-OBJ)
    assert obj.mesh_sequence_settings.name == ""
    assert obj.mesh_sequence_settings.speed == 1.0
    assert obj.mesh_sequence_settings.fileName == ""
    assert obj.mesh_sequence_settings.numMeshes == 5
    assert obj.mesh_sequence_settings.loaded is True
    assert obj.mesh_sequence_settings.meshNames == ""
    assert obj.mesh_sequence_settings.startFrame == 1
    assert obj.mesh_sequence_settings.frameMode == '4'
    assert obj.mesh_sequence_settings.initialized is True
    assert obj.mesh_sequence_settings.isImported is False
    assert obj.mesh_sequence_settings.numMeshesInMemory == 5
    assert obj.mesh_sequence_settings.meshNameArray is not None
    assert obj.mesh_sequence_settings.perFrameMaterial is False
    assert obj.mesh_sequence_settings.streamDuringPlayback is True


def test_geometry_mesh_sequence_openfoam():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = get_sample_data(utils.SAMPLE_OPENFOAM)
    
    # Test geometry
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.polygons) == mesh["faces"]
    assert len(obj.data.vertices) == mesh["vertices"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_mesh_sequence_openfoam():
    obj = bpy.data.objects.get(utils.MESH_SEQUENCE_OBJ_NAME + "_sequence", None)
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    vars = sample["variables"]["skip_zero_true"]

    # Test point data values
    for i in range(len(obj.data.vertex_colors)):
        for name, id in zip(obj.data.vertex_colors[i].name.split(', '), range(3)):
            data = obj.data.vertex_colors[i]
            ground_truth = vars[name]["mean"]
            assert abs(utils.compute_mean_value(data, obj, id) - ground_truth) < utils.PDV_THRESHOLD


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #





# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


