.. _development-environment:

Development environment
=======================


.. _development-environment-information:

General
#######

| You will need extra python packages to develop.
  What you can do is to use the python environment which comes with blender and install them there.

| Install using: ``pip install -r requirements.txt``

| We recommend you to use `Microsoft Visual Studio Code <https://code.visualstudio.com/>`__
| It offers you the possibility to use the following extensions:

.. note::

  | VSCode also lets you to choose a custom python interpreter, which can be handy.
  | Thus you can tell VSCode to use the python version which comes with blender for linting, etc.

* `Blender Development <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`__
    | Tools to simplify Blender development
* `autoDocstring - Python Docstring Generator <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>`__
    | Generates python docstrings automatically (we use the ``google`` format)
* `reStructuredText <https://marketplace.visualstudio.com/items?itemName=lextudio.restructuredtext>`__
    | reStructuredText language support (RST/ReST linter, preview, IntelliSense and more)

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


.. _development-environment-unit-testing:

Unit tests
##########

| In order to make sure new features do not break what already work, we try to maintain a high testing rate.
  We use the `blender-addon-tester <https://github.com/nangtani/blender-addon-tester>`__ python package
  along with `pytest <https://docs.pytest.org/en/7.1.x/>`__ to make our unit tests.


.. _development-environment-unit-testing-usage:

Usage
-----

| Every script that concern unit testing are under the ``scripts`` folder.
  The ``run_tests.py`` script can run all the tests for a given version of Blender.

* Arguments for ``run_tests.py``

    * -b (str, optional, defaults to ``"3.0.0"``)

        | Blender version to test

| So type the following command to run tests for a given version of Blender: ``python -m scripts.run_tests.py -b "x.x.x"``


.. _development-environment-unit-testing-write-new-tests:

Write new tests
---------------

| Please write new tests in the ``tests`` folder.
  You can either write tests in existing files (if they correspond to the theme of the file) or create a new file.
  If you need to add data for your tests, you can place it in the ``tests/data`` folder.

.. important::

    Please make sure test data are lightweight as possible, no need to have samples with hundreds of time steps and thousands of vertices.


.. _development-environment-unit-testing-pipeline:

Testing pipeline
----------------

| Here is how the unit testing pipeline is working

.. image:: /images/unit_testing.svg
    :width: 80%
    :alt: Unit testing pipeline
    :align: center
    :class: rounded-corners

|
