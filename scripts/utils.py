# <pep8 compliant>
import os
import sys
import fnmatch
import zipfile
import argparse
import subprocess


def install(package: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_requirements(requirements: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements])


def install_local_package(path: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", path])


def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    # Per https://www.tutorialspoint.com/How-to-zip-a-folder-recursively-using-Python
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# Code taken here:
# https://thispointer.com/python-how-to-remove-files-by-matching-pattern-wildcards-certain-extensions-only/
def remove_files_matching_pattern(root_folder: str, pattern: str = "*.zip") -> None:
    # Get a list of all files in directory
    for rootDir, subdirs, filenames in os.walk(root_folder):
        # Find the files that matches the given patterm
        for filename in fnmatch.filter(filenames, pattern):
            try:
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
                remove_files_matching_pattern(os.path.join(rootDir, subdir), "*.*")
                os.rmdir(os.path.join(rootDir, subdir))


# Parser for run_tests.py
parser = argparse.ArgumentParser(description="Test addon")
parser.add_argument(
    "-n",
    metavar="Name",
    type=str,
    nargs='?',
    default="src",
    help="Name to give to the zip file"
)
parser.add_argument(
    "-a",
    metavar="Addon path",
    type=str,
    nargs='?',
    default=os.path.join(os.path.abspath("."), "src"),
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
    help="Version(s) of Blender3d to test."
)
