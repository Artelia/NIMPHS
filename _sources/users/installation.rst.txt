.. _addon-installation:

Installation guide
==================

* :ref:`install-addon-linux`
* :ref:`install-addon-windows`


.. _install-addon-linux:

Linux
#####

.. important::
    This tutorial is written for Ubuntu

#. Install `Blender <https://www.blender.org/download/>`_ (at least version 3.0)

#. Install dependencies:
    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.23)
    * Python packages:

        .. important::
            You may have setup a custom python environment for Blender.
            All you have to do is to install the python packages inside your environment.

        * Go where python is installed in Blender (in ``.../3.X/python/bin/``)
        * Make sure we have pip installed: ``sudo python3.X -m ensurepip``
        * Update pip: ``sudo python3.X -m pip install -U pip``
        * Install `PyVista <https://docs.pyvista.org/#>`_ ``sudo python3.X -m pip install -U pyvista>=0.35.0 -t ../lib/site-packages/``

#. Install the add-on:
    * Download a version from the `releases page <https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/releases>`_ (latest recommended)
    * In Blender, go to ``Edit > Preferences > Add-on > Install`` and select the downloaded file
    * Do not forget to activate it (`tick the checkbox`)


.. _install-addon-windows:

Windows
#######

#. Install `Blender <https://www.blender.org/download/>`_ (at least version 3.0)

    .. important::
        If you have **administrator privileges** then you can install Blender globally.
        If not, we recommend you to **install a portable version** otherwise you may not be able
        to install python dependencies correctly.

#. Install dependencies:
    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.23)
    * Python packages:

        .. important::
            You may have setup a custom python environment for Blender.
            All you have to do is to install the python packages inside your environment.

        * Go where python is installed in Blender (in ``.../3.X/python/bin/``)
        * Make sure we have pip installed: ``.\python.exe -m ensurepip``
        * Update pip: ``.\python.exe -m pip install -U pip``
        * Install `PyVista <https://docs.pyvista.org/#>`_ ``.\python.exe -m pip install -U pyvista>=0.35.0 -t ../lib/site-packages/``

#. Install the add-on:
    * Download a version from the `releases page <https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/releases>`_ (latest recommended)
    * In Blender, go to ``Edit > Preferences > Add-on > Install`` and select the downloaded file
    * Do not forget to activate it (`tick the checkbox`)
