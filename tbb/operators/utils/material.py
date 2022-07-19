# <pep8 compliant>
import bpy
from bpy.types import Object

import logging
log = logging.getLogger(__name__)


class MaterialUtils():
    """Utility functions to generate materials for the both modules."""

    @classmethod
    def generate_preview(cls, obj: Object, name: str = "TBB_preview_material") -> None:
        """
        Generate or update the preview material.

        This generates the following node tree:

        .. code-block:: text

            {Vertex color}[color] >>> [image]{Separate RBG}[R, G, B] >>> [color]{Principled BSDF}

        Args:
            obj (Object): object on which to apply the material
            name (str, optional): name of the material. Defaults to "TBB_preview_material".
        """

        if len(obj.data.vertex_colors) <= 0:
            log.warning("No vertex color layer")
            return

        # Get the preview material
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials.new(name=name)
            material.use_nodes = True

        layer_name = obj.data.vertex_colors[0].name

        # Get node tree
        tree = material.node_tree

        vertex_color = tree.nodes.get(f"{name}_vertex_color")
        if vertex_color is None:
            vertex_color = tree.nodes.new(type="ShaderNodeVertexColor")
            vertex_color.name = f"{name}_vertex_color"
            vertex_color.location = (-500, 250)

        separate_rgb = tree.nodes.get(f"{name}_separate_rgb")
        if separate_rgb is None:
            separate_rgb = tree.nodes.new(type="ShaderNodeSeparateRGB")
            separate_rgb.name = f"{name}_separate_rgb"
            separate_rgb.location = (-250, 250)
            tree.links.new(vertex_color.outputs[0], separate_rgb.inputs[0])

        principled_bsdf = tree.nodes.get("Principled BSDF")
        # No need to remove old links thanks to the 'verify limits' argument
        tree.links.new(separate_rgb.outputs[0], principled_bsdf.inputs[0])

        # Update vertex colors group to preview
        vertex_color.layer_name = layer_name
        # Make sure it is the active material
        obj.active_material = material


class TelemacMaterialUtils(MaterialUtils):
    """Utility functions to generate materials for the TELEMAC module."""


class OpenfoamMaterialUtils(MaterialUtils):
    """Utility functions to generate materials for the OpenFOAM module."""
