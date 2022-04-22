# <pep8 compliant>
import bpy
from bpy.types import Context, Mesh, Object
from rna_prop_ui import rna_idprop_ui_create

import numpy as np


def generate_preview_object(vertices: np.array, faces: np.array, context: Context,
                            name: str) -> tuple[Mesh, Object]:
    """
    Generate a preview object from the given data.

    :param vertices: vertices, must have the following shape: (n, 3)
    :type vertices: np.array
    :param faces: faces, must have the following shape: (n, 3)
    :type faces: np.array
    :type context: Context
    :param name: name of the preview object
    :type name: str
    :return: Blender mesh (of the preview object), generated object
    :rtype: tuple[Mesh, Object]
    """

    # Create the preview object (or write over it if it already exists)
    try:
        blender_mesh = bpy.data.meshes[name + "_mesh"]
        obj = bpy.data.objects[name]
    except KeyError as error:
        print("ERROR::generate_preview_object: " + str(error))
        blender_mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, blender_mesh)
        context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return blender_mesh, obj


def update_dynamic_props(settings, new_maxima, props) -> None:
    for prop_id, prop_desc in props:
        if settings.get(prop_id) is None:
            rna_idprop_ui_create(
                settings,
                prop_id,
                default=0,
                min=0,
                soft_min=0,
                max=0,
                soft_max=0,
                description=prop_desc
            )

        prop = settings.id_properties_ui(prop_id)
        default = settings[prop_id]
        if new_maxima[prop_id] < default:
            default = 0
        prop.update(default=default, max=new_maxima[prop_id], soft_max=new_maxima[prop_id])


def remap_array(input: np.array, out_min=0.0, out_max=1.0) -> np.array:
    """
    Remap values of the given array.

    :param input: input array to remap
    :type input: np.array
    :param out_min: minimum value to output, defaults to 0.0
    :type out_min: float, optional
    :param out_max: maximum value to output, defaults to 1.0
    :type out_max: float, optional
    :return: remapped array
    :rtype: np.array
    """

    in_min = np.min(input)
    in_max = np.max(input)

    if out_min < np.finfo(np.float).eps and out_max < np.finfo(np.float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
