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


@pytest.mark.usefixtures("clean_all_objects")
def test_reload_file_data_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Get and select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)

    op = bpy.ops.tbb.reload_openfoam_file
    assert op('EXEC_DEFAULT') == {'FINISHED'}

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test file_data
    assert file_data.time_point == 0
    assert file_data.module == 'OpenFOAM'
    assert file_data.vars.dumps() == utils.get_point_data_openfoam(True).dumps()
    assert file_data.nb_time_points == sample["values"]["skip_zero_true"]["nb_time_points"]
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.mesh, pyvista.UnstructuredGrid)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_reload_file_data_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Get and select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    op = bpy.ops.tbb.reload_telemac_file
    assert op('EXEC_DEFAULT') == {'FINISHED'}

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.vars.length() == sample["nb_vars"]
    assert file_data.nb_planes == sample["nb_planes"]
    assert file_data.is_3d() is sample["is_3d"]
    assert file_data.faces is not None
    assert file_data.module == 'TELEMAC'
    assert file_data.nb_time_points == sample["nb_time_points"]
    assert file_data.vertices is not None
    assert file_data.nb_vertices == sample["mesh"]["vertices"]
    assert file_data.nb_triangles == sample["mesh"]["triangles"]
    assert file_data.vars.dumps() == utils.get_point_data_telemac('2D').dumps()


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_reload_file_data_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    # Get and select preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    op = bpy.ops.tbb.reload_telemac_file
    assert op('EXEC_DEFAULT') == {'FINISHED'}

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Test file data
    assert file_data.vars.length() == sample["nb_vars"]
    assert file_data.nb_planes == sample["nb_planes"]
    assert file_data.is_3d() is sample["is_3d"]
    assert file_data.faces is not None
    assert file_data.module == 'TELEMAC'
    assert file_data.nb_time_points == sample["nb_time_points"]
    assert file_data.vertices is not None
    assert file_data.nb_vertices == sample["mesh"]["vertices"]
    assert file_data.nb_triangles == sample["mesh"]["triangles"]
    assert file_data.vars.dumps() == utils.get_point_data_telemac('3D').dumps()
