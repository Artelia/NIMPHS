# <pep8 compliant>
import pytest
from blender_addon_tester.addon_helper import get_version


@pytest.fixture
def bpy_module(cache):
    return cache.get("bpy_module", None)


def test_addon_version(bpy_module):
    expect_version = (0, 3, 0)
    return_version = get_version(bpy_module)
    assert expect_version == return_version
