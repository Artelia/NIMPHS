.. _developer-documentation-introduction:

Introduction
============


.. _addon-file-architecture:

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

| Most of these folders contain one folder per module (the folder is then named with the module's name).
| Moreover, you may find these folders in all parent folders:

  * ``utils``: contains utility functions used in all modules.
  * ``shared``: contains code used in all modules.


.. _addon-auto-loader:

Auto-loader
###########

| This addon is loaded using an 'autoloader' helper.
  This is one is mostly inspired from the 'autoloader' used in `animation nodes <https://github.com/JacquesLucke/animation_nodes>`_.

| Consequently, every folder in the source directory must contain an ``__init__.py`` file.

| For each class, you need to define two attributes:

* The ``register_cls`` attribute (bool), indicates if this class has to be registered.
* The ``is_custom_base_cls`` attribute (bool), indicates if this class is a custom base class of other classes.


.. _addon-coding-style:

Coding style
############

| We try to follow as close as possible the `coding style <https://wiki.blender.org/wiki/Style_Guide/Python>`_ proposed by the Blender development team.
| Python code should adhere to `PEP 8 <https://peps.python.org/pep-0008/>`_ (with some exceptions, see the link above).
