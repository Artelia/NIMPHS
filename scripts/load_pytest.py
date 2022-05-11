# <pep8 compliant>
# Custom tests loader and runner for Blender's Python environment
print("Running file:", __file__, "from Blender")

import os
import sys
from pathlib import Path

sys.path.append(os.path.relpath("."))
from scripts.utils import install, install_requirements, install_local_package, remove_files_matching_pattern

try:
    import pytest
except Exception as e:
    print(e)
    sys.exit(1)


# Make sure to have BLENDER_ADDON_TO_TEST set as an environment variable first
ADDON = os.environ.get("BLENDER_ADDON_TO_TEST", False)
if not ADDON:
    print("ERROR: no addon to test was found in the 'BLENDER_ADDON_TO_TEST' environment variable.")
    sys.exit(1)

# Set any value to the BLENDER_ADDON_COVERAGE_REPORTING environment variable to enable it
COVERAGE_REPORTING = os.environ.get("BLENDER_ADDON_COVERAGE_REPORTING", False)

# The Pytest tests/ path can be overriden through the BLENDER_ADDON_TESTS_PATH environment variable
default_tests_dir = Path(ADDON).parent.joinpath("tests")
TESTS_PATH = os.environ.get("BLENDER_ADDON_TESTS_PATH", default_tests_dir.as_posix())

# Install addon requirements
try:
    install_requirements(os.path.join(os.path.relpath("."), "requirements.txt"))
except Exception as e:
    print(e)
    sys.exit(1)

# Temporary workaround to install a local custom version of pyvista and vtk
# Reasons: no vtk support for pytyon 3.10+ and a small edit in pyvista which will be available later
try:
    from bpy.app import version
    if version > (3, 0, 0):
        install("https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl")
    install_local_package(os.path.join(os.path.relpath("./../"), "pyvista"))
except Exception as e:
    print(e)
    sys.exit(1)

# Not the best solution but it works.
# Blender_addon_tester should not be installed in the Blender python folder.
# We should be able to add it through this line: sys.path.append(os.environ["LOCAL_PYTHONPATH"])
try:
    import blender_addon_tester
except BaseException:
    pass

if "blender_addon_tester" not in globals():
    try:
        print("Blender_addon_tester not found. Installaing...")
        install("blender_addon_tester")
    except Exception as e:
        print(e)
        sys.exit(1)
else:
    print("Blender_addon_tester already installed.")

# Import utils functions
from blender_addon_tester.addon_helper import zip_addon, change_addon_dir, install_addon, cleanup


# Setup class for PyTest
class SetupPlugin:
    def __init__(self, addon):
        self.root = Path(__file__).parent.parent
        self.addon = addon
        self.addon_dir = "local_addon"
        self.bpy_module = None
        self.zfile = None

    def pytest_configure(self, config):
        print("PyTest configure...")

        (self.bpy_module, self.zfile) = zip_addon(self.addon, self.addon_dir)
        change_addon_dir(self.bpy_module, self.addon_dir)
        install_addon(self.bpy_module, self.zfile)
        config.cache.set("bpy_module", self.bpy_module)

        print("PyTest configuration successfull!")

    def pytest_unconfigure(self):
        print("PyTest unconfigure...")

        cleanup(self.addon, self.bpy_module, self.addon_dir)
        # Cleanup zip files
        remove_files_matching_pattern(self.root)

        print("PyTest unconfiguration successfull!")


try:
    pytest_main_args = [TESTS_PATH, "-v", "-x"]
    if COVERAGE_REPORTING is not False:
        pytest_main_args += ["--cov", "--cov-report", "term", "--cov-report", "xml"]
    exit_val = pytest.main(pytest_main_args, plugins=[SetupPlugin(ADDON)])
except Exception as e:
    print(e)
    exit_val = 1
sys.exit(exit_val)
