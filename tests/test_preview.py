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
    op = bpy.ops.nimphs.import_openfoam_file
    assert op('EXEC_DEFAULT', mode='TEST', filepath=utils.FILE_PATH_OPENFOAM, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()
    assert obj is not None

    # Set preview settings
    io_settings = obj.nimphs.settings.openfoam.import_settings
    io_settings.triangulate = False
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = False

    assert obj.nimphs.settings.openfoam.import_settings.triangulate is False

    assert bpy.ops.nimphs.openfoam_preview('EXEC_DEFAULT', mode='TEST') == {'FINISHED'}


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
    io_settings = obj.nimphs.settings.openfoam.import_settings
    io_settings.triangulate = False
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = True

    assert bpy.ops.nimphs.openfoam_preview('EXEC_DEFAULT', mode='TEST') == {'FINISHED'}


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
    io_settings = obj.nimphs.settings.openfoam.import_settings
    io_settings.triangulate = True
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = False

    assert bpy.ops.nimphs.openfoam_preview('EXEC_DEFAULT', mode='TEST') == {'FINISHED'}


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
    io_settings = obj.nimphs.settings.openfoam.import_settings
    io_settings.triangulate = True
    io_settings.skip_zero_time = False
    io_settings.case_type = 'reconstructed'
    io_settings.decompose_polyhedra = True

    assert bpy.ops.nimphs.openfoam_preview('EXEC_DEFAULT', mode='TEST') == {'FINISHED'}


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


def test_preview_point_data_openfoam():
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    var_name = sample["preview"]["name"]

    # Set point data to preview
    obj.nimphs.settings.preview_time_point = sample["preview"]["time_point"]
    obj.nimphs.settings.preview_point_data = utils.get_point_data_openfoam(False).get(var_name).dumps()

    assert bpy.ops.nimphs.openfoam_preview('EXEC_DEFAULT', mode='TEST') == {'FINISHED'}


def test_point_data_preview_object_openfoam():
    # Check preview object
    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    var_name = sample["preview"]["name"]
    assert obj is not None

    # Check number vertex colors arrays
    vertex_colors = obj.data.vertex_colors
    assert len(vertex_colors) == 1

    # Test point data values
    data = vertex_colors.get(f"{var_name}, None, None", None)
    assert data is not None

    ground_truth = sample["values"]["skip_zero_false"][var_name]["mean"]
    utils.compare_point_data_value(utils.compute_mean_value(data, obj, 0) - ground_truth, var_name)


@pytest.mark.usefixtures("clean_all_objects")
def test_preview_material_openfoam():
    sample = utils.get_sample_data(utils.SAMPLE_OPENFOAM)
    var_name = sample["preview"]["name"]
    material_name = "OpenFOAM_preview_material"

    # Test preview material
    material = bpy.data.materials.get(material_name, None)
    assert material is not None
    assert material.use_nodes is True

    # Test nodes
    principled_bsdf = material.node_tree.nodes.get("Principled BSDF", None)
    assert principled_bsdf is not None
    vertex_color = material.node_tree.nodes.get(f"{material_name}_vertex_color", None)
    assert vertex_color is not None
    assert vertex_color.layer_name == f"{var_name}, None, None"
    separate_rgb = material.node_tree.nodes.get(f"{material_name}_separate_rgb", None)
    assert separate_rgb is not None
    output = material.node_tree.nodes.get("Material Output", None)
    assert output is not None

    # Test links
    link = material.node_tree.links[0]
    assert link.from_node == principled_bsdf
    assert link.from_socket == principled_bsdf.outputs[0]
    assert link.to_node == output
    assert link.to_socket == output.inputs[0]
    link = material.node_tree.links[1]
    assert link.from_node == vertex_color
    assert link.from_socket == vertex_color.outputs[0]
    assert link.to_node == separate_rgb
    assert link.to_socket == separate_rgb.inputs[0]
    link = material.node_tree.links[2]
    assert link.from_node == separate_rgb
    assert link.from_socket == separate_rgb.outputs[0]
    assert link.to_node == principled_bsdf
    assert link.to_socket == principled_bsdf.inputs[0]


# -------------------------- #
#         TELEMAC 2D         #
# -------------------------- #


def test_preview_telemac_2d():
    # Import TELEMAC 2D sample object
    op = bpy.ops.nimphs.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_2D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    var_name = sample["preview"]["name"]
    assert obj is not None

    # Set preview settings
    obj.nimphs.settings.preview_time_point = sample["preview"]["time_point"]
    obj.nimphs.settings.preview_point_data = utils.get_point_data_telemac('2D').get(var_name).dumps()

    assert bpy.ops.nimphs.telemac_preview('EXEC_DEFAULT') == {'FINISHED'}


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
    var_name = sample["preview"]["name"]

    for child in obj.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        data = vertex_colors.get(f"{var_name}, None, None", None)
        assert data is not None

        # Test point data values
        ground_truth = sample["values"][var_name]["mean"]
        utils.compare_point_data_value(utils.compute_mean_value(data, child, 0) - ground_truth, var_name)


# -------------------------- #
#         TELEMAC 3D         #
# -------------------------- #


def test_preview_telemac_3d():
    # Import TELEMAC 3D sample object
    op = bpy.ops.nimphs.import_telemac_file
    assert op('EXEC_DEFAULT', filepath=utils.FILE_PATH_TELEMAC_3D, name=utils.PRW_OBJ_NAME) == {'FINISHED'}

    obj = utils.get_preview_object()
    sample = utils.get_sample_data(utils.SAMPLE_TELEMAC_2D)
    var_name = sample["preview"]["name"]
    assert obj is not None

    # Set preview settings
    obj.nimphs.settings.preview_time_point = sample["preview"]["time_point"]
    obj.nimphs.settings.preview_point_data = utils.get_point_data_telemac('3D').get(var_name).dumps()

    assert bpy.ops.nimphs.telemac_preview('EXEC_DEFAULT') == {'FINISHED'}


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
    var_name = sample["preview"]["name"]

    # SPMV = Sum partial mean values
    spmv = 0.0

    for child in obj.children:
        # Check number vertex colors arrays
        vertex_colors = child.data.vertex_colors
        assert len(vertex_colors) == 1

        data = vertex_colors.get(f"{var_name}, None, None", None)
        assert data is not None

        # Test point data values
        spmv += utils.compute_mean_value(data, child, 0)

    ground_truth = sample["values"][var_name]["spmv"]
    utils.compare_point_data_value(abs(spmv - ground_truth), var_name)
