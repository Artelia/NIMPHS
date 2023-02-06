# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import sys
import json
import subprocess


class NIMPHS_OT_ResetInstaller(Operator):
    """Reset installer state to let the user install dependencies again."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.reset_installer"
    bl_label = "Reset installer"
    bl_description = "Reset installer state so you can install dependencies again"

    def execute(self, context: Context) -> set:
        """
        Reset installer state.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        # Replace value inside json file
        with open(context.scene.nimphs_state_file, "r+", encoding='utf-8') as file:
            data = json.load(file)

        data["installation"]["state"] = 'INSTALL'

        with open(context.scene.nimphs_state_file, "w", encoding='utf-8') as file:
            json.dump(data, file)

        return {'FINISHED'}


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

        settings = context.preferences.addons['nimphs'].preferences.settings

        # Make sure we have pip available
        args = [sys.executable, "-m", "ensurepip"]
        subprocess.check_call(args)

        # Upgrade pip
        args = [sys.executable, "-m", "pip", "install", "--upgrade"]

        # Try to install 'ADVANCED' packages first
        if settings.configuration == 'ADVANCED':

            try:
                self.install_package('numba', directory=context.scene.site_packages, force=settings.reinstall)
                self.install_package('multiprocessing', directory=context.scene.site_packages, force=settings.reinstall)
            except Exception as exception:
                message = ("\n\n"
                           "An error occurred during installation with 'ADVANCED' configuration.\n")

                log.error(message + str(exception))

                return {'CANCELLED'}

        # Then, install packages for the 'CLASSIC' configuration
        try:
            self.install_requirements(
                settings.requirements,
                directory=context.scene.site_packages,
                force=settings.reinstall)
        except Exception as exception:
            message = ("\n\n"
                       "An error occurred during installation.\n")

            log.error(message + str(exception))

            return {'CANCELLED'}

        # Replace value inside json file to indicate installation is complete
        with open(context.scene.nimphs_state_file, "r+", encoding='utf-8') as file:
            data = json.load(file)

        data["installation"]["state"] = 'DONE'

        with open(context.scene.nimphs_state_file, "w", encoding='utf-8') as file:
            json.dump(data, file)

        return {'FINISHED'}

    def install_package(self, package: str, directory: str = '', force: bool = False) -> None:
        """
        Install the given python package.

        Args:
            package (str): name of the python package.
            directory (str, optional): specify a directory where to install the package.
            force (bool, optional): force reinstall. Defaults to False.
        """

        args = [sys.executable, "-m", "pip", "install", package]
        if force:
            args.append("--force-reinstall")
        if directory != '':
            args.append("-t")
            args.append(directory)

        subprocess.check_call(args)

    def install_requirements(self, requirements: str, directory: str = '', force: bool = False) -> None:
        """
        Install python packages from the given requirements file.

        Args:
            requirements (str): path to the requirements file.
            directory (str, optional): specify a directory where to install packages.
            force (bool, optional): force reinstall. Defaults to False.
        """

        args = [sys.executable, "-m", "pip", "install", "-r", requirements, "-U"]
        if force:
            args.append("--force-reinstall")
        if directory != '':
            args.append("-t")
            args.append(directory)

        subprocess.check_call(args)
