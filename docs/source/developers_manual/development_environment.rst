.. _development_environment:

Development environment
=======================

* :ref:`general_dev_env`
* :ref:`tests_dev_env`

.. _general_dev_env:

General
#######

| You will need the following python packages to develop:

* `PyVista <https://docs.pyvista.org/#>`_ ``pip install pyvista`` (python 3.10 workaround `here <https://github.com/pyvista/pyvista/discussions/2064>`_)
* `Numpy <https://numpy.org/doc/stable/#>`_ ``pip install numpy``
* `fake-bpy-module <https://pypi.org/project/fake-bpy-module-latest/>`_
* `sphinx <https://pypi.org/project/Sphinx/>`_, install using ``pip install sphinx`` or ``apt install sphinx`` (for Ubuntu)
* `sphinxemoji <https://pypi.org/project/sphinxemoji/>`_
* `sphinx_rtd_theme <https://pypi.org/project/sphinx-rtd-theme/>`_

| We recommend you to use `Microsoft Visual Studio Code <https://code.visualstudio.com/>`_
| It offers you the possibility to use the following extensions:

* `Blender Development <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`_
    | Tools to simplify Blender development
* `autoDocstring - Python Docstring Generator <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_
    | Generates python docstrings automatically (we use the ``google`` format)
* `reStructuredText <https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext>`_
    | reStructuredText language support (RST/ReST linter, preview, IntelliSense and more)
* `Run on save <https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave>`_
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

| You can also setup the `autopep8 <https://code.visualstudio.com/docs/python/editing#_formatting>`_ tool which will automatically format your code.
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

| We use the `blender-addon-tester <https://github.com/nangtani/blender-addon-tester>`_ python package along with `pytest <https://docs.pytest.org/en/7.1.x/>`_ to make our unit tests.

Setup
-----

* Install the ``blender-addon-tester`` python package: ``pip install blender-addon-tester``

.. important::

    The latest version of `pyvista <https://github.com/pyvista/pyvista>`_ does not contain features that were added since the latest release `(v.0.34.0)`.
    Therefore, you must clone the github repository next to the addon's folder. Make sure to checkout the `main` branch.
    The tests scripts will use this version instead of the versions available through PyPi.

Usage
-----

| Every scripts that concern unit testing are under the ``scripts`` folder.
| The ``run_tests.py`` script can run all the tests for a given version of Blender.

* Arguments for ``run_tests.py``

    * -a
  
        | Hello

Write new tests
---------------

