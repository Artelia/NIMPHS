# <pep8 compliant>
import bpy
from bpy.types import Object

import logging
log = logging.getLogger(__name__)


class TelemacMaterialUtils():

    @classmethod
    def generate_preview(cls, obj: Object, var_name: str, name: str = "TBB_TELEMAC_preview_material") -> None:
        """
        Generate or update the preview material.

        This generates the following node tree:

        .. code-block:: text

            {Vertex color}[color] >>> [image]{Separate RBG}[R, G, B] >>> [color]{Principled BSDF}

        Args:
            obj (Object): object on which to apply the material
            var_name (str): name of the variable to preview
            name (str, optional): name of the material. Defaults to "TBB_TELEMAC_preview_material".

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
            for name, chan_id in zip(names, range(len(names))):
                if name == var_name:
                    channel_id, group_name = chan_id, group.name

        if channel_id == -1:
            raise NameError("Variable " + str(var_name) + " not found in vertex colors data")

        # Get node tree
        mat_node_tree = material.node_tree

        vertex_color_node = mat_node_tree.nodes.get(name + "_vertex_color")
        if vertex_color_node is None:
            vertex_color_node = mat_node_tree.nodes.new(type="ShaderNodeVertexColor")
            vertex_color_node.name = name + "_vertex_color"
            vertex_color_node.location = (-500, 250)

        separate_rgb_node = mat_node_tree.nodes.get(name + "_separate_rgb")
        if separate_rgb_node is None:
            separate_rgb_node = mat_node_tree.nodes.new(type="ShaderNodeSeparateRGB")
            separate_rgb_node.name = name + "_separate_rgb"
            separate_rgb_node.location = (-250, 250)
            mat_node_tree.links.new(vertex_color_node.outputs[0], separate_rgb_node.inputs[0])

        principled_bsdf_node = mat_node_tree.nodes.get("Principled BSDF")
        # No need to remove old links thanks to the 'verify limits' argument
        mat_node_tree.links.new(separate_rgb_node.outputs[channel_id], principled_bsdf_node.inputs[0])

        # Update vertex colors group to preview
        vertex_color_node.layer_name = group_name
        # Make sure it is the active material
        obj.active_material = material


class OpenfoamMaterialUtils():

    @classmethod
    def generate_preview(cls, obj: Object, scalar: str, name: str = "TBB_OpenFOAM_preview_material") -> None:
        """
        Generate or update the preview material.

        Args:
            obj (Object): object on which to apply the material
            scalar (str): name of the vertex colors group to preview
            name (str, optional): name of the preview material. Defaults to "TBB_OpenFOAM_preview_material".
        """

        # Get the preview material
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials.new(name=name)
            material.use_nodes = True

        # Get node tree
        mat_node_tree = material.node_tree
        vertex_color_node = mat_node_tree.nodes.get(name + "_vertex_color")
        if vertex_color_node is None:
            # If the node does not exist, create it and link it to the shader
            vertex_color_node = mat_node_tree.nodes.new(type="ShaderNodeVertexColor")
            vertex_color_node.name = name + "_vertex_color"
            principled_bsdf_node = mat_node_tree.nodes.get("Principled BSDF")
            mat_node_tree.links.new(vertex_color_node.outputs[0], principled_bsdf_node.inputs[0])
            vertex_color_node.location = (-200, 250)

        # Update scalar to preview
        vertex_color_node.layer_name = ""
        if scalar != 'None':
            vertex_color_node.layer_name = scalar
        # Make sure it is the active material
        obj.active_material = material
