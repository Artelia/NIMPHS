# <pep8 compliant>
import os
import sys
import bpy
import pytest

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils
# Fixtures
from helpers.utils import clean_all_objects


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


@pytest.mark.usefixtures("clean_all_objects")
def test_edit_file_path_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.edit_file_path
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM) == {'FINISHED'}


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_edit_file_path_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.edit_file_path
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D) == {'FINISHED'}


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


@pytest.mark.usefixtures("clean_all_objects")
def test_edit_file_path_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()  # noqa: F841

    op = bpy.ops.tbb.edit_file_path
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D) == {'FINISHED'}
