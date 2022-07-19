# <pep8 compliant>
import bpy
from bpy.types import Object

import logging
log = logging.getLogger(__name__)


class MaterialUtils():

    @classmethod
    def generate_preview(cls, obj: Object, var_name: str, name: str = "TBB_preview_material") -> None:
        """
        Generate or update the preview material.

        This generates the following node tree:

        .. code-block:: text

            {Vertex color}[color] >>> [image]{Separate RBG}[R, G, B] >>> [color]{Principled BSDF}

        Args:
            obj (Object): object on which to apply the material
            var_name (str): name of the variable to preview
            name (str, optional): name of the material. Defaults to "TBB_preview_material".

        Raises:
            NameError: if the variable is not found in the vertex colors groups
        """

        # Get the preview material
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials.new(name=name)
            material.use_nodes = True

        # Get channel and vertex colors group for the given variable name
        channel_id, group_name = -1, ""
        for group in obj.data.vertex_colors:
            names = group.name.split(", ")
            for var, chan_id in zip(names, range(len(names))):
                if var == var_name:
                    channel_id, group_name = chan_id, group.name

        if channel_id == -1:
            raise NameError(f"Point data {var_name} not found in vertex colors data")

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
        tree.links.new(separate_rgb.outputs[channel_id], principled_bsdf.inputs[0])

        # Update vertex colors group to preview
        vertex_color.layer_name = group_name
        # Make sure it is the active material
        obj.active_material = material


class TelemacMaterialUtils(MaterialUtils):
    """Utility functions to generate materials for the TELEMAC module."""


class OpenfoamMaterialUtils(MaterialUtils):
    """Utility functions to generate materials for the OpenFOAM module."""
