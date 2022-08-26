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


def test_remove_point_data_openfoam():
    pytest.skip(reason="Not implemented yet")


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
