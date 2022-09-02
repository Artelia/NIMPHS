.. _addon-installation:

Installation
============

* :ref:`install-addon-linux`
* :ref:`install-addon-windows`


.. _install-addon-linux:

Linux
#####

.. important::
    This tutorial is written for Ubuntu

#. Install `Blender <https://www.blender.org/download/>`_ (at least version 3.0)

#. Install dependencies:

    .. note::
        You may have setup a custom python environment for Blender.
        All you have to do is to install the python packages inside your environment.

    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.23)
    * Python packages:

        * Go where python is installed in Blender (in ``.../3.X/python/bin/``)
        * Make sure we have pip installed: ``sudo ./python3.X -m ensurepip``
        * Update pip: ``sudo ./python3.X -m pip install -U pip``
        * Install `PyVista <https://docs.pyvista.org/#>`_ ``sudo ./python3.X -m pip install -U pyvista -t ../lib/python3.X/site-packages/``

            .. important::
                Next points are only needed if you are planning to generate volume sequences from TELEMAC-3D files.

        * Install `Numba <https://numba.pydata.org/numba-doc/latest/index.html>`_ (for CUDA support) ``sudo ./python3.X -m pip install -U numba -t ../lib/python3.X/site-packages/``
        * Install `pyopenvdb <https://github.com/AcademySoftwareFoundation/openvdb>`_. There is no "simple" way for the moment.
          We are waiting for `this PR <https://github.com/AcademySoftwareFoundation/openvdb/pull/1377>`_ to be merged. This should make the process a lot easier.
          
          |     For now, you have to install it by your own means. You probably will have to install `boost <https://www.boost.org/>`_ and `tbb <https://github.com/oneapi-src/oneTBB>`_.
          |     Here are some steps to help you install it manually:

          * Download latest release of `OpenVDB <https://github.com/AcademySoftwareFoundation/openvdb/releases>`_
          * Run: ``cd openvdb && mkdir build && cd build``
          * Run: ``cmake -DOPENVDB_BUILD_PYTHON_MODULE=ON -DUSE_NUMPY=ON -DPython_EXECUTABLE=path/to/python/bin/python3.X ..``
          * Run: ``sudo make -j 8 && sudo make install``

#. Install the add-on:
    * Download a version from the `releases page <https://github.com/Artelia/NIMPHS/releases>`_ (latest recommended)
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

    .. note::
        You may have setup a custom python environment for Blender.
        All you have to do is to install the python packages inside your environment.

    * Blender add-on: `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_ (at least version 2.2.0.alpha.23)
    * Python packages:

        * Go where python is installed in Blender (in ``.../3.X/python/bin/``)
        * Make sure we have pip installed: ``.\python.exe -m ensurepip``
        * Update pip: ``.\python.exe -m pip install -U pip``
        * Install `PyVista <https://docs.pyvista.org/#>`_ ``.\python.exe -m pip install -U pyvista -t ../lib/site-packages/``

            .. important::
                Next points are only needed if you are planning to generate volume sequences from TELEMAC-3D files.

        * Install `Numba <https://numba.pydata.org/numba-doc/latest/index.html>`_ (for CUDA support) ``.\python.exe -m pip install -U numba -t ../lib/site-packages/``
        * Install `pyopenvdb <https://github.com/AcademySoftwareFoundation/openvdb>`_. There is no "simple" way for the moment.
          We are waiting for `this PR <https://github.com/AcademySoftwareFoundation/openvdb/pull/1377>`_ to be merged. This should make the process a lot easier.
          
          |     For now, you have to install it by your own means. You probably will have to install `boost <https://www.boost.org/>`_ and `tbb <https://github.com/oneapi-src/oneTBB>`_.
          |     [TODO]
          
#. Install the add-on:
    * Download a version from the `releases page <https://github.com/Artelia/NIMPHS/releases>`_ (latest recommended)
    * In Blender, go to ``Edit > Preferences > Add-on > Install`` and select the downloaded file
    * Do not forget to activate it (`tick the checkbox`)
