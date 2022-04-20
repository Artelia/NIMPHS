Introduction
============

* :ref:`file_architecture`
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

| Each of these folders contain an ``OpenFOAM`` folder and a ``TELEMAC`` folder.
| These contain all the code for each module.

| If some code is used by both module, you can place it at the root folder.
| Example: ``src/panels/custom_progress_bar.py``

.. _coding_style:

Coding style
############

| We try to follow as close as possible the `coding style <https://wiki.blender.org/wiki/Style_Guide/Python>`_ proposed by the Blender development team.
| Python code should adhere to `PEP 8 <https://peps.python.org/pep-0008/>`_ (with some exceptions, see the link above).

.. _development_environment:

Development environment
#######################

| We recommend you to use `Microsoft Visual Studio Code <https://code.visualstudio.com/>`_
| It offers you the possibility to use the following extensions:

* `Blender Development <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`_
    | Tools to simplify Blender development
* `autoDocstring - Python Docstring Generator <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`_
    | Generates python docstrings automatically
* `reStructuredText <https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext>`_
    | reStructuredText language support (RST/ReST linter, preview, IntelliSense and more)

| You can also setup the `autopep8 <https://code.visualstudio.com/docs/python/editing#_formatting>`_ tool which will automatically format your code.
| We use the following autopep8 arguments:

.. code-block:: json

    "python.formatting.autopep8Args": [
        "--max-line-length",
        "120",
        "--aggressive"
    ],