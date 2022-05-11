# <pep8 compliant>
import os
import sys
import zipfile
from pathlib import Path

from scripts.utils import zipdir, parser, remove_folders_matching_pattern

try:
    import blender_addon_tester as BAT
except Exception as e:
    print(e)
    sys.exit(1)


def main():
    arguments = parser.parse_args()
    # Get addon path

    if arguments.n is None:
        print("ERROR: -n option is None.")
        parser.parse_args(['-h'])

    name = arguments.n

    if arguments.a is None:
        print("ERROR: -a option is None.")
        parser.parse_args(['-h'])

    addon = arguments.a

    # Get blender version(s) to test the addon
    if arguments.b is None:
        print("ERROR: -b option is None.")
        parser.parse_args(['-h'])

    blender_rev = arguments.b

    try:
        # Cleanup '__pychache__' folders in the 'src' folder
        remove_folders_matching_pattern(os.path.join(os.path.relpath("."), "src"))

        # Zip addon
        print("Zipping addon - " + name)
        zipf = zipfile.ZipFile(name + ".zip", 'w', zipfile.ZIP_DEFLATED)
        zipdir("./" + name, zipf)
        zipf.close()

    except Exception as e:
        print(e)
        exit_val = 1

    addon = os.path.join(os.path.abspath("."), name + ".zip")

    # Custom configuration
    here = Path(__file__).parent
    config = {
        "blender_load_tests_script": here.joinpath("load_pytest.py").as_posix(),
        "coverage": False,
        "tests": here.joinpath("../tests").as_posix(),
        "blender_cache": here.joinpath("../cache").as_posix()
    }

    try:
        # Setup custom blender cache (where the blender versions will be downloaded and extracted)
        # The blender_addon_tester module raises an error when passed as a key in the config dict
        if config.get("blender_cache", None):
            os.environ["BLENDER_CACHE"] = config["blender_cache"]
            config.pop("blender_cache")

        exit_val = BAT.test_blender_addon(addon_path=addon, blender_revision=blender_rev, config=config)
    except Exception as e:
        print(e)
        exit_val = 1

    sys.exit(exit_val)


main()
