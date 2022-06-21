# <pep8 compliant>
# Code taken here: https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/auto_load.py
# Slightly edited
import bpy
import typing
import inspect
import pkgutil
import importlib
import numpy as np
from pathlib import Path

__all__ = (
    "init",
    "register",
    "unregister",
)

modules = None
ordered_classes = None


def init():
    global modules
    global ordered_classes

    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)


def register():
    for cls in ordered_classes:
        bpy.utils.register_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()


def unregister():
    for cls in reversed(ordered_classes):
        bpy.utils.unregister_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()


# Import modules
#################################################

def get_all_submodules(directory):
    return list(iter_submodules(directory, directory.name))


def iter_submodules(path, package_name):
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)


def iter_submodule_names(path, root=""):
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################

def get_ordered_classes_to_register(modules):
    return toposort(get_register_deps_dict(modules))


def get_register_deps_dict(modules):
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")}

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(iter_my_register_deps(cls, my_classes, my_classes_by_idname))
    return deps_dict


def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)


def iter_my_deps_from_annotations(cls, my_classes):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency


def get_dependency_from_annotation(value):
    if isinstance(value, bpy.props._PropertyDeferred):
        return value.keywords.get("type")
    return None


def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    cls_inherits_from_custom_base_class = bpy.types.Panel in np.array(
        [base.__bases__ for base in cls.__bases__]).flatten()

    if bpy.types.Panel in cls.__bases__ or cls_inherits_from_custom_base_class:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls


def iter_my_classes(modules):
    base_types = get_register_base_types(modules)
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if getattr(cls, "register_cls", False) and not getattr(cls, "is_registered", False):
                yield cls


def get_classes_in_modules(modules):
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes


def iter_classes_in_module(module):
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value


def get_register_base_types(modules):
    return set(getattr(bpy.types, name) for name in [
        "Panel", "Operator", "PropertyGroup",
        "AddonPreferences", "Header", "Menu",
        "Node", "NodeSocket", "NodeTree",
        "UIList", "RenderEngine"
    ]).union(get_custom_base_types(modules))


def get_custom_base_types(modules):
    names = set()
    for cls in get_classes_in_modules(modules):
        is_base_cls = getattr(cls, "is_custom_base_cls", None)
        if is_base_cls is not None and is_base_cls:
            names.add(cls)

    return names


# Find order to register to solve dependencies
#################################################

def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list
