Introduction
============

* :ref:`file_architecture`
* :ref:`auto_loader`
* :ref:`coding_style`

.. _file_architecture:

File architecture
#################

| The file architecture is as follows:

* An ``icons`` folder
    | Here you can put custom icons (PNGs, 16x16px and 32x32px)
* A ``menus`` folder
    | Contains all the menus
* An ``operators`` folder
    | Contains all the operators
* A ``panels`` folder
    | Contains all UI classes with which the user interacts
* A ``properties`` folder
    | Contains all the properties definitions

| Most of these folders contain an ``openfoam`` folder, a ``telemac`` folder and a ``shared`` folder.
| These contain all the code for each module. The ``shared`` folder contains code used in both modules.

.. _auto_loader:

Auto-loader
###########

| This addon is loaded using an 'autoloader' helper.
  This is one is mostly inspired from the 'autoloader' used in `animation nodes <https://github.com/JacquesLucke/animation_nodes>`_.

| Consequently, every folder in the ``tbb`` directory must contain an ``__init__.py`` file.

| For each class, you need to define two attributes:

* The ``register_cls`` attribute (bool), indicates if this class has to be registered
* The ``is_custom_base_cls`` attribute (bool), indicates if this class is a custom base class of other classes

.. _coding_style:

Coding style
############

| We try to follow as close as possible the `coding style <https://wiki.blender.org/wiki/Style_Guide/Python>`_ proposed by the Blender development team.
| Python code should adhere to `PEP 8 <https://peps.python.org/pep-0008/>`_ (with some exceptions, see the link above).