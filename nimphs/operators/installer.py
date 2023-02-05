# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import os
import sys
import subprocess
from pathlib import Path


class NIMPHS_OT_Installer(Operator):
    """Run installation from the installation panel located into Add-on's preferences."""

    register_cls = False
    is_custom_base_cls = False

    bl_idname = "nimphs.install"
    bl_label = "Install"
    bl_description = "Run the installation process depending on the chosen configuration"

    def execute(self, context: Context) -> set:
        """
        Run installation process.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        file_path = os.path.join(os.path.abspath(Path(__file__).parent.parent), "requirements.txt")
        settings = context.preferences.addons['nimphs'].preferences.settings

        # Try to install 'ADVANCED' packages first
        if settings.configuration == 'ADVANCED':

            try:
                self.install_package('numba', force=settings.reinstall)
                self.install_package('multiprocessing', force=settings.reinstall)
            except Exception as exception:
                message = ("\n\n"
                           "An error occurred during installation with 'ADVANCED' configuration.\n")

                log.error(message + str(exception))

        # Then, install packages for the 'CLASSIC' configuration
        try:
            self.install_requirements(file_path, force=settings.reinstall)
        except Exception as exception:
            message = ("\n\n"
                       "An error occurred during installation.\n")

            log.error(message + str(exception))

        return {'FINISHED'}

    def install_package(self, package: str, force: bool = False) -> None:
        """
        Install the given python package.

        Args:
            package (str): name of the python package.
            force (bool, optional): force reinstall. Defaults to False.
        """
        args = [sys.executable, "-m", "pip", "install", package]
        if force:
            args.append("--force-reinstall")
        subprocess.check_call(args)

    def install_requirements(self, requirements: str, force: bool = False) -> None:
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
