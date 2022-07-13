# <pep8 compliant>
import os
import sys
import bpy
import json
import pytest
import pyvista
import numpy as np

# Make helpers module available in this file
sys.path.append(os.path.abspath("."))
from helpers import utils


# ------------------------ #
#         OpenFOAM         #
# ------------------------ #


def test_import_openfoam():
    op = bpy.ops.tbb.import_openfoam_file

    # Test with wrong filepath
    assert op('EXEC_DEFAULT', filepath="test.foam", name=utils.PREVIEW_OBJ_NAME) == {'CANCELLED'}

    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME) == {'FINISHED'}


def test_imported_object_openfoam():
    # Check imported object
    obj = utils.get_preview_object()
    assert obj is not None

    # Get sample data
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)

    # Test geometry
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["triangles"]

    # Test object properties
    assert obj.tbb.uid != ""
    assert obj.tbb.module == 'OpenFOAM'
    assert obj.tbb.is_mesh_sequence is False
    assert obj.tbb.is_streaming_sequence is False

    # Test object settings
    assert obj.tbb.settings.file_path == utils.FILE_PATH_OPENFOAM


def test_file_data_imported_object_openfoam():
    obj = utils.get_preview_object()

    # Get file_data
    file_data = bpy.context.scene.tbb.file_data.get(obj.tbb.uid, None)
    assert file_data is not None

    # Get sample data
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)

    # Test file data
    assert file_data.time_point == 0
    assert file_data.vars is not None
    assert file_data.module == 'OpenFOAM'
    assert file_data.nb_time_points == sample["variables"]["skip_zero_true"]["nb_time_points"]
    assert isinstance(file_data.mesh, pyvista.PolyData)
    assert isinstance(file_data.file, pyvista.OpenFOAMReader)
    assert isinstance(file_data.raw_mesh, pyvista.UnstructuredGrid)


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #