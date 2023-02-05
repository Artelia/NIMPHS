.. _addon-installation:

Installation
============

#. Install `Blender <https://www.blender.org/download/>`_ (at least version 3.0)

#. Install dependencies:

    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.23)

#. Install NIMPHS:

    * Download a version from the `releases page <https://github.com/Artelia/NIMPHS/releases>`_ (latest recommended)
    * Open Blender, go to ``Edit > Preferences > Add-on > Install`` and select the downloaded file
    * Activate it (`tick the checkbox`)
    * Go under preferences and select an installation configuration:

        * ``CLASSIC``: this is the basic and recommended configuration.
        * ``ADVANCED``: configuration which will let you install other dependencies to use under-development features.
        * `Force` (option): install python pyckages with the ``--force-reinstall`` flag on.

    * Then, click on the ``install`` button.

        .. image:: /images/installation/run_install_process.png
            :width: 55%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * |  If everything went well, you should see this message. Then, just reopen Blender and voilà! |:magic_wand:|
      |  If not, the error message should be printed in the console.

        .. image:: /images/installation/post_run_install_process.png
            :width: 55%
            :alt: Preview panel
            :align: center
            :class: rounded-corners


Reinstall python dependencies
=============================

    .. note::
        If you need to reinstall the python dependencies or switch configuration, follow these instructions.

    * Open Blender, go to ``Edit > Preferences > Add-on``
    * Then, click on the ``Re-install`` button

        .. image:: /images/installation/reset_installer_state.png
            :width: 55%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * Then, follow the instructions and do the same process as in step ``3. Install NIMPHS``.

        .. image:: /images/installation/post_reset_installer_state.png
            :width: 55%
            :alt: Preview panel
            :align: center
            :class: rounded-corners
