# <pep8 compliant>
import os
import sys
import shutil
import fnmatch
import zipfile
import requests
import argparse
import subprocess


class Colors:
    """List of color which can be used to color texts in the terminal."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def centered_str(message: str, char: str = "-") -> str:
    """
    Generate a line full of 'char' with the given message at the center.

    Args:
        message (str): message to display.
        char (str, optional): char with which to fill the line. Defaults to "-".

    Returns:
        str: generated line
    """
    terminal_size = shutil.get_terminal_size((80, 20))
    return message.center(terminal_size.columns, char)


def install(package: str, force: bool = False) -> None:
    """
    Install the given package.

    Args:
        package (str): name of the package.
        force (bool, optional): force reinstall. Defaults to False.
    """
    args = [sys.executable, "-m", "pip", "install", package]
    if force:
        args.append("--force-reinstall")
    subprocess.check_call(args)


def install_requirements(requirements: str, force: bool = False) -> None:
    """
    Install python packages from the given requirements file.

    Args:
        requirements (str): path to the requirements file.
        force (bool, optional): force reinstall. Defaults to False.
    """
    args = [sys.executable, "-m", "pip", "install", "-r", requirements, "-U"]
    if force:
        args.append("--force-reinstall")
    subprocess.check_call(args)


def install_local_package(path: str, force: bool = False) -> None:
    """
    Install a local package.

    Args:
        path (str): path to the folder of the local package.
        force (bool, optional): force reinstall. Defaults to False.
    """
    args = [sys.executable, "-m", "pip", "install", "-e", path]
    if force:
        args.append("--force-reinstall")
    subprocess.check_call(args)


def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    """
    Zip the given folder.

    Args:
        path (str): path to the folder.
        ziph (zipfile.ZipFile): zip file.
    """
    # Inspired from: https://www.tutorialspoint.com/How-to-zip-a-folder-recursively-using-Python
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# Inspired from:
# https://thispointer.com/python-how-to-remove-files-by-matching-pattern-wildcards-certain-extensions-only/
def remove_files_matching_pattern(root_folder: str, exclude_folders: list[str] = [], pattern: str = "*.zip") -> None:
    """
    Remove files which name match the given pattern.

    Args:
        root_folder (str): root folder.
        exclude_folders (list[str], optional): list of folders to exclude from this function. Defaults to [].
        pattern (str, optional): pattern of the files to remove. Defaults to "*.zip".
    """
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
    """
    Remove folders which name match the given pattern.

    Args:
        root_folder (str): root folder.
        pattern (str, optional): pattern of the folders to remove. Defaults to "__pycache__".
    """
    # Get a list of all files in directory
    for rootDir, subdirs, filenames in os.walk(root_folder):
        # Find the files that matches the given patterm
        for subdir in subdirs:
            if subdir == pattern:
                # First, remove all files inside the folder
                remove_files_matching_pattern(os.path.join(rootDir, subdir), pattern="*.*")
                os.rmdir(os.path.join(rootDir, subdir))


def download_stop_motion_obj_addon(dest: str, version: str = "v2.2.0.alpha.23") -> tuple[str, str]:
    """
    Download the Stop-Motion-OBJ addon.

    Args:
        dest (str): destination of the downloaded file.
        version (str, optional): version to download. Defaults to "v2.2.0.alpha.23".

    Returns:
        tuple[str, str]: path to the zip file, name of the module.
    """

    module_name = "Stop-motion-OBJ"
    filename = f"{module_name}-{version}.zip"
    path = os.path.abspath(os.path.join(dest, filename))

    if (not os.path.exists(dest)):
        print(f"The given path does not exist: {dest}")
        os.mkdir(dest)
        print(f"Created destination folder: {dest}")

    if (os.path.exists(os.path.join(dest, filename))):
        print(f"Stop-Motion-OBJ - found: {path}")
        return path, module_name

    # Else, download it and save it at the given destination
    print(f"Downloading: {filename}")
    url = f"https://github.com/neverhood311/Stop-motion-OBJ/releases/download/{version}/"
    response = requests.get(url + filename)
    open(os.path.join(dest, filename), "wb").write(response.content)

    return path, module_name


# Parser for run_tests.py
parser = argparse.ArgumentParser(description="Test addon")
parser.add_argument(
    "-b",
    metavar="Blender version",
    type=str,
    nargs='?',
    default="3.0.0",
    help="Version of Blender to test."
)
