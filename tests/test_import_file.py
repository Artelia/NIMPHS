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
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_import_openfoam():
    op = bpy.ops.nimphs.import_openfoam_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="test.foam", name=utils.PRW_OBJ_NAME) == {'CANCELLED'}

    assert op('EXEC_DEFAULT', mode='TEST', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PRW_OBJ_NAME) == {'FINISHED'}


def test_imported_object_openfoam():
    # Check imported object
    obj = utils.get_preview_object()
    assert obj is not None

    # Test geometry
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["triangles"]

    # Test object properties
    assert obj.nimphs.uid != ""
    assert obj.nimphs.module == 'OpenFOAM'
    assert obj.nimphs.is_mesh_sequence is False
    assert obj.nimphs.is_streaming_sequence is False
    assert obj.nimphs.settings.file_path == utils.FILE_PATH_OPENFOAM


@pytest.mark.usefixtures("clean_all_objects")
def test_file_data_imported_object_openfoam():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    point_data = utils.get_point_data_openfoam(True)

    # Get file_data
    file_data = bpy.context.scene.nimphs.file_data.get(obj.nimphs.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.time_point == 0
    assert file_data.module == 'OpenFOAM'
    assert file_data.vars.names == point_data.names
    assert file_data.vars.units == point_data.units
    assert file_data.nb_time_points == sample["values"]["skip_zero_true"]["nb_time_points"]
    assert isinstance(file_data.mesh, pyvista.PolyData)
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_import_telemac_2d():
    op = bpy.ops.nimphs.import_telemac_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="test.slf", name=utils.PRW_OBJ_NAME) == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}


def test_file_data_imported_object_telemac_2d():
    pytest.skip(reason="Not implemented yet")


@pytest.mark.usefixtures("clean_all_objects")
def test_imported_object_telemac_2d():
    # Check imported object
    obj = utils.get_preview_object()
    assert obj is not None
    assert len(obj.children) == 2

    # Test geometry
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]
        assert len(child.data.polygons) == sample["mesh"]["triangles"]

    # Test object properties
    assert obj.nimphs.uid != ""
    assert obj.nimphs.module == 'TELEMAC'
    assert obj.nimphs.is_mesh_sequence is False
    assert obj.nimphs.is_streaming_sequence is False


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_import_telemac_3d():
    op = bpy.ops.nimphs.import_telemac_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="test.slf", name=utils.PRW_OBJ_NAME) == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}


def test_file_data_imported_object_telemac_3d():
    pytest.skip(reason="Not implemented yet")


@pytest.mark.usefixtures("clean_all_objects")
def test_imported_object_telemac_3d():
    # Check imported object
    obj = utils.get_preview_object()
    assert obj is not None
    assert len(obj.children) == 3

    # Test geometry
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]
        assert len(child.data.polygons) == sample["mesh"]["triangles"]

    # Test object properties
    assert obj.nimphs.uid != ""
    assert obj.nimphs.module == 'TELEMAC'
    assert obj.nimphs.is_mesh_sequence is False
    assert obj.nimphs.is_streaming_sequence is False
