Introduction
============

* :ref:`file_architecture`
* :ref:`auto_loader`
* :ref:`coding_style`
* :ref:`development_environment`

.. _file_architecture:

File architecture
##################

| The file architecture is as follows:

* An ``operators`` folder
    | Contains all the operators
* A ``panels`` folder
    | Contains all UI classes with which the user interacts
* A ``properties`` folder
    | Contains all the properties definitions

| Each of these folders contain an ``openfoam`` folder, a ``telemac`` folder and a ``shared`` folder.
| These contain all the code for each module. The ``shared`` folder contains code used in both modules.

.. _auto_loader:

Auto-loader
###########

| This addon is loaded using an 'autoloader' helper. This is one is mostly inspired from the 'autoloader' used in `animation nodes <https://github.com/JacquesLucke/animation_nodes>`_.

| Consequently, every folder in the ``src`` directory must contain an empty ``__init__.py`` file.

| For each class, you need to defined two attributes:

* The ``register_cls`` attribute (bool), indicates if this class has to be registerd
* The ``is_custom_base_cls`` attribute (bool), indicates if this class is a custom base class of other classes

.. _coding_style:

Coding style
############

| We try to follow as close as possible the `coding style <https://wiki.blender.org/wiki/Style_Guide/Python>`_ proposed by the Blender development team.
| Python code should adhere to `PEP 8 <https://peps.python.org/pep-0008/>`_ (with some exceptions, see the link above).

.. _development_environment:

Development environment
#######################

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
    | Generates python docstrings automatically, we use the ``google`` format
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

| Using VSCode also let you to choose a custum python interpreter, which can be handy.