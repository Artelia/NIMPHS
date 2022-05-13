.. _development_environment:

Development environment
=======================

* :ref:`general_dev_env`
* :ref:`tests_dev_env`

.. _general_dev_env:

General
#######

| You will need the following python packages to develop:

* `PyVista <https://docs.pyvista.org/#>`__ ``pip install pyvista`` (python 3.10 workaround `here <https://github.com/pyvista/pyvista/discussions/2064>`__)
* `Numpy <https://numpy.org/doc/stable/#>`__ ``pip install numpy``
* `fake-bpy-module <https://pypi.org/project/fake-bpy-module-latest/>`_
* `sphinx <https://pypi.org/project/Sphinx/>`__, install using ``pip install sphinx`` or ``apt install sphinx`` (for Ubuntu)
* `sphinxemoji <https://pypi.org/project/sphinxemoji/>`__
* `sphinx_rtd_theme <https://pypi.org/project/sphinx-rtd-theme/>`__

| We recommend you to use `Microsoft Visual Studio Code <https://code.visualstudio.com/>`__
| It offers you the possibility to use the following extensions:

* `Blender Development <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`__
    | Tools to simplify Blender development
* `autoDocstring - Python Docstring Generator <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`__
    | Generates python docstrings automatically (we use the ``google`` format)
* `reStructuredText <https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext>`__
    | reStructuredText language support (RST/ReST linter, preview, IntelliSense and more)
* `Run on save <https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave>`__
    | Run commands when a file is saved in vscode. You can use the following configuration:
    
    .. code-block:: json

        "emeraldwalk.runonsave": {
            "autoClearConsole": true,
            "commands": [
                {
                    "match": "\\.rst$",
                    "isAsync": true,
                    "cmd": "cd docs && make html"
                }
            ]
        }

| You can also setup the `autopep8 <https://code.visualstudio.com/docs/python/editing#_formatting>`__ tool which will automatically format your code.
| We use the following autopep8 arguments:

.. code-block:: json

    "python.formatting.autopep8Args": [
        "--max-line-length",
        "120",
        "--aggressive",
        "--ignore",
        "E402"
    ],

| Using VSCode also let you to choose a custom python interpreter, which can be handy.

.. _tests_dev_env:

Unit tests
##########

| In order to make sure new features do not break what already work, we try to maintain a high testing rate.

| We use the `blender-addon-tester <https://github.com/nangtani/blender-addon-tester>`__ python package along with `pytest <https://docs.pytest.org/en/7.1.x/>`__ to make our unit tests.

Setup
-----

* Install the ``blender-addon-tester`` python package: ``pip install blender-addon-tester``

.. important::

    The latest version of `pyvista <https://github.com/pyvista/pyvista>`__ does not contain features that were added since the latest release `(v.0.34.0)`.
    Therefore, you must clone the github repository next to the addon's folder. Make sure to checkout the `main` branch.
    The tests scripts will use this version instead of the versions available through PyPi.

Usage
-----

| Every scripts that concern unit testing are under the ``scripts`` folder.
| The ``run_tests.py`` script can run all the tests for a given version of Blender.

* Arguments for ``run_tests.py``

    * -a (str, optional, defaults to ``"[current_directory]/src"`` then you have to run this script for the root folder (`toolsbox_blender`))
  
        | Addon path to test, can be a path to a directory or a .zip file.

    * -n (str, optional, default to ``"src"``)

        | Name to give to the zip file (in case the path to the addon is a directory)

    * -b (str, optional, defaults to ``"3.0.0"``)

        | Blender version to test

| So type the following command to run tests for a given version of Blender (make sure you are in the ``toolsbox_blender`` folder): ``python -m scripts.run_tests.py -b "x.x.x"``


Write new tests
---------------

| Please write new tests in the ``tests`` folder.
| You can either write tests in existing files (if they correspond to the theme of the file) or create a new file.

| If you need to add data for your tests, you can place it in the ``tests/data`` folder.

.. important::

    Please make sure they are lightweight as possible, no need to have samples with hundreds of time steps and thousands of vertices.


Testing pipeline
----------------

| Here is how the unit testing pipeline is working

.. image:: /images/unit_testing.svg
    :width: 80%
    :alt: Unit testing pipeline
    :align: center