Linux
=====

.. important::
    This tutorial is written for Ubuntu

#. Install `Blender <https://www.blender.org/download/>`_ (at least version 3.0)
#. Install dependencies:
    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.18)
    * Python packages:

        .. important::
            You may have setup a custom python environment for Blender. All you have to do is to install the python packages inside you environment.

        * `PyVista <https://docs.pyvista.org/#>`_ ``pip install pyvista`` (python 3.10 workaround `here <https://github.com/pyvista/pyvista/discussions/2064>`_)
        * `Numpy <https://numpy.org/doc/stable/#>`_ ``pip install numpy``
#. Install the add-on:
    * Download a version from the `releases page <https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/releases>`_ (latest recommended)
    * In Blender, go to ``Edit > Preferences > Add-on > Install`` and select the downloaded file
    * Do not forget to activate it (`tick the checkbox`)