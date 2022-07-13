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


def test_add_point_data_openfoam():
    pytest.skip(reason="Not implemented yet")
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


def test_remove_point_data_openfoam():
    pytest.skip(reason="Not implemented yet")
    # TODO: First fix add_point_data test. Then complete this one.
    file_data = bpy.context.scene.tbb.file_data.get(preview_object.tbb.uid, None)
    assert file_data is not None


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_add_point_data_telemac_2d():
    pytest.skip(reason="Not implemented yet")


def test_remove_point_data_telemac_2d():
    pytest.skip(reason="Not implemented yet")


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_add_point_data_telemac_3d():
    pytest.skip(reason="Not implemented yet")


def test_remove_point_data_telemac_3d():
    pytest.skip(reason="Not implemented yet")