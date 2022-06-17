# <pep8 compliant>
from bpy.types import Operator, Context
from bpy.props import StringProperty, EnumProperty

import logging
from tbb.panels.utils import get_selected_object
from tbb.properties.utils import VariablesInformation
log = logging.getLogger(__name__)

from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_OT_RemovePointData(Operator):
    """Remove point data from the list to import as vertex colors."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.remove_point_data"
    bl_label = "Remove point data"
    bl_description = "Remove point data from the list to import as vertex colors"

    #: bpy.props.StringProperty: Name of the variable to remove.
    var_name: StringProperty(
        name="Variable name",
        description="Name of the variable to remove",
        default="",
    )

    #: bpy.props.EnumProperty: Indicates the activator of this operator.
    #  Enum in ['OBJECT', 'OPERATOR/OpenFOAM', 'OPERATOR/TELEMAC'].
    source: EnumProperty(
        name="Source",  # noqa F821
        description="Indicates the activator of this operator.\
Enum in ['OBJECT', 'OPERATOR/OpenFOAM', 'OPERATOR/TELEMAC']",
        items=[
            ("OBJECT", "Object", "Execute in object mode"),  # noqa F821
            ("OPERATOR/OpenFOAM", "Operator (OpenFOAM)", "Execute in operator mode, OpenFOAM module"),  # noqa F821
            ("OPERATOR/TELEMAC", "Operator (TELEMAC)", "Execute in operator mode, TELEMAC module"),  # noqa F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    def execute(self, context: Context) -> set:
        """
        Remove point data from the list using the given name.

        Args:
            context (Context): context
            name (str): name of point data

        Returns:
            set: state of the operator
        """

        # Get point data
        if self.source == 'OBJECT':
            obj = get_selected_object(context)
            if obj is None:
                log.warning("No selected object.", exc_info=1)
                return {'CANCELLED'}

            point_data = obj.tbb.settings.point_data.list

        if self.source == 'OPERATOR/OpenFOAM':
            # TODO: I think we can find a better solution to get access to these data.
            import bpy
            point_data = bpy.types.TBB_OT_openfoam_create_mesh_sequence.list
        if self.source == 'OPERATOR/TELEMAC':
            # TODO: I think we can find a better solution to get access to these data.
            import bpy
            point_data = bpy.types.TBB_OT_telemac_create_mesh_sequence.list

        # Remove selected point data from the list
        data = VariablesInformation(point_data)
        data.remove(data.names.index(self.var_name))

        # Save the new list of chosen point data
        if self.source == 'OBJECT':
            obj.tbb.settings.point_data.list = data.dumps()
        if self.source == 'OPERATOR/OpenFOAM':
            bpy.types.TBB_OT_openfoam_create_mesh_sequence.list = data.dumps()
        if self.source == 'OPERATOR/TELEMAC':
            bpy.types.TBB_OT_telemac_create_mesh_sequence.list = data.dumps()

        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}
