# <pep8 compliant>
from bpy.props import EnumProperty
from bpy.types import Operator, Context

import logging

from nimphs.operators.utils.mesh import OpenfoamMeshUtils
from nimphs.operators.utils.object import OpenfoamObjectUtils
from nimphs.operators.utils.material import OpenfoamMaterialUtils
from nimphs.operators.utils.vertex_color import OpenfoamVertexColorUtils
log = logging.getLogger(__name__)

import time

from nimphs.panels.utils import get_selected_object


class NIMPHS_OT_OpenfoamPreview(Operator):
    """Operator to generate a preview of an OpenFOAM object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "nimphs.openfoam_preview"
    bl_label = "Preview"
    bl_description = "Preview the selected object"

    #: bpy.props.EnumProperty: Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST'].
    mode: EnumProperty(
        name="Mode",                                    # noqa: F821
        description="Indicate which mode to use for this operator. Enum in ['NORMAL', 'TEST']",
        items=[
            ('NORMAL', "Normal", "Run normal"),         # noqa: F821
            ('TEST', "Test", "Run for unit tests"),     # noqa: F821
        ],
        options={'HIDDEN'},                             # noqa: F821
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        Check if the operator can run.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        obj = get_selected_object(context)
        if obj is None:
            return False

        file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)
        return file_data is not None and file_data.is_ok()

    def execute(self, context: Context) -> set:
        """
        Generate a preview of the selected object.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        # Get settings
        obj = get_selected_object(context)
        clip = obj.nimphs.settings.openfoam.clip
        io_settings = obj.nimphs.settings.openfoam.import_settings
        file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)

        if clip.type != "" and clip.scalar.name == "None":
            self.report({'WARNING'}, "Select a scalar to clip on. You may need to reload the file if none are shown")
            return {'FINISHED'}

        prw_time_point = obj.nimphs.settings.preview_time_point

        # Generate mesh data
        try:
            file_data.update_import_settings(io_settings)
            file_data.update_data(prw_time_point)
            vertices, file_data.mesh = OpenfoamMeshUtils.vertices(file_data, clip)
            faces = OpenfoamMeshUtils.faces(file_data.mesh)
        except Exception:
            log.debug("Something went wrong building the mesh", exc_info=1)
            self.report({'WARNING'}, "Something went wrong building the mesh")
            return {'CANCELLED'}

        # Generate object
        try:
            obj = OpenfoamObjectUtils.generate(vertices, faces, obj.name_full)
            if context.collection.name not in [col.name for col in obj.users_collection]:
                context.collection.objects.link(obj)
        except Exception:
            log.debug("Something went generating the object", exc_info=1)
            self.report({'WARNING'}, "Something went wrong generating the object")
            return {'CANCELLED'}

        # Import point data as vertex colors
        point_data = obj.nimphs.settings.preview_point_data
        if point_data is not None and point_data != 'NONE':
            data = OpenfoamVertexColorUtils.prepare(obj.data, point_data, file_data)
            if not data.is_empty():
                OpenfoamVertexColorUtils.generate(obj.data, data)
                OpenfoamMaterialUtils.generate_preview(obj, name="OpenFOAM_preview_material")

        try:
            # Update point data local value ranges
            if self.mode != 'TEST':
                for name in file_data.vars.names:
                    file_data.update_var_range(name, data=file_data.get_point_data_from_raw(name))
        except BaseException:
            log.warning("An error occurred updating point data local value range.", exc_info=1)

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Preview done")

        return {'FINISHED'}
