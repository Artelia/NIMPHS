# <pep8 compliant>
from bpy.types import Operator, Context

import logging
log = logging.getLogger(__name__)

import time

from tbb.panels.utils import get_selected_object
from tbb.operators.utils import generate_object_from_data, generate_vertex_colors
from tbb.operators.openfoam.utils import generate_mesh_data, prepare_openfoam_point_data, generate_preview_material


class TBB_OT_OpenfoamPreview(Operator):
    """Operator to generate a preview of an OpenFOAM object."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_preview"
    bl_label = "Preview"
    bl_description = "Preview the selected object"

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

        file_data = context.scene.tbb.file_data.get(obj.tbb.uid, None)
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
        collection = context.scene.collection
        clip = obj.tbb.settings.openfoam.clip
        io_settings = obj.tbb.settings.openfoam.import_settings
        file_data = context.scene.tbb.file_data.get(obj.tbb.uid, None)

        if clip.type != "" and clip.scalar.name == "None":
            self.report({'WARNING'}, "Select a scalar to clip on. You may need to reload the file if none are shown")
            return {'FINISHED'}

        prw_time_point = obj.tbb.settings.preview_time_point

        # Generate mesh data
        try:
            file_data.update_data(prw_time_point, io_settings)
            vertices, faces, file_data.mesh = generate_mesh_data(file_data, clip=clip)
        except Exception:
            log.debug("Something went wrong building the mesh", exc_info=1)
            self.report({'WARNING'}, "Something went wrong building the mesh")
            return {'CANCELLED'}

        # Generate object
        try:
            obj = generate_object_from_data(vertices, faces, "TBB_OpenFOAM_preview")
            if collection.name not in [col.name for col in obj.users_collection]:
                collection.objects.link(obj)
        except Exception:
            log.debug("Something went generating the object", exc_info=1)
            self.report({'WARNING'}, "Something went generating the object")
            return {'CANCELLED'}

        # Import point data as vertex colors
        point_data = obj.tbb.settings.preview_point_data
        if point_data is not None and point_data != 'NONE':
            res = prepare_openfoam_point_data(obj.data, point_data, file_data)
            if len(res[0]) > 0:
                generate_vertex_colors(obj.data, *res)
                generate_preview_material(obj, res[0][0]["name"] if len(res[0]) > 0 else 'None')

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Preview done")

        return {'FINISHED'}
