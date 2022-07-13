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


def test_normal_preview_object_openfoam():
    # Import OpenFOAM sample object
    op = bpy.ops.tbb.import_openfoam_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PREVIEW_OBJ_NAME)  == {'FINISHED'}

    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    io_settings = obj.tbb.settings.openfoam.import_settings
    io_settings.triangulate = False
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = False

    assert obj.tbb.settings.openfoam.import_settings.triangulate is False

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_normal_preview_object():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    assert obj is not None

    # Test geometry
    mesh = sample["mesh"]["normal"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["faces"]


def test_normal_decompose_polyhedra_preview_object_openfoam():
    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    io_settings = obj.tbb.settings.openfoam.import_settings
    io_settings.triangulate = False
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = True

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_normal_decompose_polyhedra_preview_object_openfoam():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    assert obj is not None

    # Test geometry
    mesh = sample["mesh"]["normal"]["decompose_polyhedra"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["faces"]


def test_triangulated_preview_object_openfoam():
    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    io_settings = obj.tbb.settings.openfoam.import_settings
    io_settings.triangulate = True
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = False

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_triangulated_preview_object_openfoam():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    assert obj is not None

    # Test geometry
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["faces"]


def test_triangulated_decompose_polyhedra_preview_object_openfoam():
    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    io_settings = obj.tbb.settings.openfoam.import_settings
    io_settings.triangulate = True
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = True

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_triangulated_decompose_polyhedra_preview_object_openfoam():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    assert obj is not None

    # Test geometry
    mesh = sample["mesh"]["triangulated"]["normal"]
    assert len(obj.data.edges) == mesh["edges"]
    assert len(obj.data.vertices) == mesh["vertices"]
    assert len(obj.data.polygons) == mesh["faces"]


def test_preview_point_data():
    obj = utils.get_preview_object()

    # Set point data to preview
    obj.tbb.settings.preview_time_point = 2
    obj.tbb.settings.preview_point_data = json.dumps(utils.get_point_data_openfoam(False).get("nut"))

    assert bpy.ops.tbb.openfoam_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_point_data_preview_object_openfoam():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    assert obj is not None

    # Check number vertex colors arrays
    vertex_colors = obj.data.vertex_colors
    assert len(vertex_colors) == 1

    # Test point data values
    data = vertex_colors.get("nut, None, None", None)
    assert data is not None

    ground_truth = sample["variables"]["skip_zero_false"]["nut"]["mean"]
    assert abs(utils.compute_mean_value(data, obj, 0) - ground_truth) < utils.PDV_THRESHOLD


@pytest.mark.usefixtures("clean_all_objects")
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
    assert vertex_color_node.layer_name == "nut, None, None"

    # Test links
    link = prw_mat.node_tree.links[-1]
    assert link.from_node == vertex_color_node
    assert link.from_socket == vertex_color_node.outputs[0]
    assert link.to_node == principled_bsdf_node
    assert link.to_socket == principled_bsdf_node.inputs[0]


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_preview_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PREVIEW_OBJ_NAME)  == {'FINISHED'}

    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    obj.tbb.settings.preview_time_point = 5
    obj.tbb.settings.preview_point_data = json.dumps(utils.get_point_data_telemac('2D').get("VELOCITY U"))

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_preview_object_telemac_2d():
    obj = utils.get_preview_object()

    # Test geometry
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]
        assert len(child.data.polygons) == sample["mesh"]["triangles"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_preview_object_telemac_2d():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)

    for child in obj.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        velocity_u = vertex_colors.get("VELOCITY U, None, None", None)
        assert velocity_u is not None

        # Test point data values
        ground_truth = sample["variables"]["VELOCITY U"]["mean"]
        assert abs(utils.compute_mean_value(velocity_u, child, 0) - ground_truth) < utils.PDV_THRESHOLD


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_preview_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.tbb.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PREVIEW_OBJ_NAME)  == {'FINISHED'}

    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    obj.tbb.settings.preview_time_point = 5
    obj.tbb.settings.preview_point_data = json.dumps(utils.get_point_data_telemac('3D').get("VELOCITY U"))

    assert bpy.ops.tbb.telemac_preview('EXEC_DEFAULT') == {'FINISHED'}


def test_geometry_preview_object_telemac_3d():
    obj = utils.get_preview_object()

    # Test geometry
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)
    for child in obj.children:
        assert len(child.data.edges) == sample["mesh"]["edges"]
        assert len(child.data.vertices) == sample["mesh"]["vertices"]
        assert len(child.data.polygons) == sample["mesh"]["triangles"]


@pytest.mark.usefixtures("clean_all_objects")
def test_point_data_preview_object_telemac_3d():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_3D)

    # SPMV = Sum partial mean values
    spmv = 0.0

    for child in obj.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        velocity_u = vertex_colors.get("VELOCITY U, None, None", None)
        assert velocity_u is not None

        # Test point data values
        spmv += utils.compute_mean_value(velocity_u, child, 0)

    ground_truth = sample["variables"]["VELOCITY U"]["spmv"]
    assert abs(spmv - ground_truth) < utils.PDV_THRESHOLD
