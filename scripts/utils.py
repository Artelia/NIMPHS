# <pep8 compliant>
from ast import arg
import os
import sys
import shutil
import fnmatch
import zipfile
import requests
import argparse
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_centered_message(message: str, char: str = "-") -> str:
    terminal_size = shutil.get_terminal_size((80, 20))
    return message.center(terminal_size.columns, char)


def install(package: str, force: bool = False) -> None:
    args = [sys.executable, "-m", "pip", "install", package]
    if force:
        args.append("--force-reinstall")
    subprocess.check_call(args)


def install_requirements(requirements: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements])


def install_local_package(path: str, force: bool = False) -> None:
    args = [sys.executable, "-m", "pip", "install", "-e", path]
    if force:
        args.append("--force-reinstall")
    subprocess.check_call(args)


def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    # Per https://www.tutorialspoint.com/How-to-zip-a-folder-recursively-using-Python
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# Code taken here:
# https://thispointer.com/python-how-to-remove-files-by-matching-pattern-wildcards-certain-extensions-only/
def remove_files_matching_pattern(root_folder: str, exclude_folders: list[str] = [], pattern: str = "*.zip") -> None:
    # Get a list of all files in directory
    for rootDir, subdirs, filenames in os.walk(root_folder):
        # Find the files that matches the given patterm
        for filename in fnmatch.filter(filenames, pattern):
            try:
                if os.path.dirname(os.path.join(rootDir, filename)) not in exclude_folders:
                    os.remove(os.path.join(rootDir, filename))
            except OSError:
                print("Error while deleting file")


def remove_folders_matching_pattern(root_folder: str, pattern: str = "__pycache__") -> None:
    # Get a list of all files in directory
    for rootDir, subdirs, filenames in os.walk(root_folder):
        # Find the files that matches the given patterm
        for subdir in subdirs:
            if subdir == pattern:
                # First, remove all files inside the folder
                remove_files_matching_pattern(os.path.join(rootDir, subdir), pattern="*.*")
                os.rmdir(os.path.join(rootDir, subdir))


def download_stop_motion_obj_addon(dest: str, version: str = "v2.2.0.alpha.18") -> tuple[str, str]:
    module_name = "Stop-motion-OBJ"
    filename = module_name + "-" + version + ".zip"
    path = os.path.abspath(os.path.join(dest, filename))

    if (not os.path.exists(dest)):
        raise AttributeError("The given path does not exist:", dest)

    if (os.path.exists(os.path.join(dest, filename))):
        print("Stop-Motion-OBJ - found:", path)
        return path, module_name

    # Else, download it and save it at the given destination
    print("Downloading:", filename)
    url = "https://github.com/neverhood311/Stop-motion-OBJ/releases/download/" + version + "/"
    response = requests.get(url + filename)
    open(os.path.join(dest, filename), "wb").write(response.content)

    return path, module_name


# Parser for run_tests.py
parser = argparse.ArgumentParser(description="Test addon")
parser.add_argument(
    "-n",
    metavar="Name",
    type=str,
    nargs='?',
    default="tbb",
    help="Name to give to the zip file"
)
parser.add_argument(
    "-a",
    metavar="Addon path",
    type=str,
    nargs='?',
    default=os.path.join(os.path.abspath("."), "tbb"),
    help="Addon path to test, can be a path to a directory (will be zipped for you) or to a .zip file.\
        The Python module name will be that of the (directory or) zip file without extension,\
        try to make it as pythonic as possible for Blender's Python importer to work properly\
        with it: letters, digits, underscores."
)
parser.add_argument(
    "-b",
    metavar="Blender version",
    type=str,
    nargs='?',
    default="3.0.0",
    help="Version of Blender to test."
)
