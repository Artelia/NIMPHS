# <pep8 compliant>
# Custom tests loader and runner for Blender's Python environment
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath("."))  # Make utils.py functions available in this file
from scripts.utils import install_requirements, remove_files_matching_pattern, Colors, centered_str

print(f"{Colors.OKBLUE}{centered_str(' LOAD PYTEST ', '=')}{Colors.ENDC}")
print("Running file:", __file__, "from Blender")

# Make sure to have BLENDER_ADDON_TO_TEST set as an environment variable first
ADDON = os.environ.get("BLENDER_ADDON_TO_TEST", False)
if not ADDON:
    print("ERROR: no addon to test was found in the 'BLENDER_ADDON_TO_TEST' environment variable.")
    sys.exit(1)

# Set any value to the BLENDER_ADDON_COVERAGE_REPORTING environment variable to enable it
COVERAGE_REPORTING = os.environ.get("BLENDER_ADDON_COVERAGE_REPORTING", False)

# The Pytest tests/ path can be overridden through the BLENDER_ADDON_TESTS_PATH environment variable
default_tests_dir = Path(ADDON).parent.joinpath("tests")
TESTS_PATH = os.environ.get("BLENDER_ADDON_TESTS_PATH", default_tests_dir.as_posix())

# Install addon requirements
try:
    import pytest
    import pyvista
    import matplotlib
    import blender_addon_tester
except Exception:
    try:
        install_requirements(os.path.join(os.path.abspath("./scripts"), "requirements.txt"))
    except Exception as e:
        print(e)
        sys.exit(1)

# Import utils functions
import blender_addon_tester.addon_helper as BAT

# Setup class for PyTest
class SetupPlugin:
    """Setup class for pytest."""

    def __init__(self, addon: str):
        """
        Init method of the class.

        Args:
            addon (sstr): absolute path to the addon (zip file)
        """

        self.root = Path(__file__).parent.parent
        self.addon = addon
        self.addon_dir = "local_addon"
        self.bpy_module = None
        self.zfile = None

    def pytest_configure(self, config: dict):
        """
        Configure pytest.

        Args:
            config (dict): configuration
        """

        print("PyTest configure...")

        (self.bpy_module, self.zfile) = BAT.zip_addon(self.addon, self.addon_dir)
        BAT.change_addon_dir(self.bpy_module, self.addon_dir)
        BAT.install_addon(os.environ.get("STOP_MOTION_OBJ_MODULE", None), os.environ.get("STOP_MOTION_OBJ_PATH", None))
        BAT.install_addon(self.bpy_module, self.zfile)
        config.cache.set("bpy_module", self.bpy_module)

        print("PyTest configure successful!")

    def pytest_unconfigure(self):
        """Unconfigure pytest."""

        print("PyTest unconfigure...")

        BAT.cleanup(self.addon, self.bpy_module, self.addon_dir)
        BAT.cleanup(self.addon, os.environ.get("STOP_MOTION_OBJ_MODULE", None), self.addon_dir)
        
        # Cleanup zip files
        print("Cleaning up - zip files")
        remove_files_matching_pattern(self.root, exclude_folders=[os.path.abspath("./cache")], pattern="*.zip")

        print("PyTest unconfigure successful!")


try:
    import pytest

    pytest_main_args = ["-x", TESTS_PATH]
    if COVERAGE_REPORTING is not False:
        pytest_main_args += ["--cov", "--cov-report", "term", "--cov-report", "xml"]
    exit_val = pytest.main(pytest_main_args, plugins=[SetupPlugin(ADDON)])

except Exception as e:
    print(e)
    exit_val = 1
    
sys.exit(exit_val)
