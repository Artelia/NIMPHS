# <pep8 compliant>
from bpy.types import Operator, Context

import time
import logging
log = logging.getLogger(__name__)

from tbb.operators.utils import generate_object_from_data, generate_vertex_colors
from tbb.operators.openfoam.utils import (
    generate_mesh_data,
    prepare_openfoam_point_data,
    generate_preview_material)
from tbb.panels.utils import get_selected_object


class TBB_OT_OpenfoamPreview(Operator):
    """Preview the mesh using the loaded file and selected parameters."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

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

        tmp_data = context.scene.tbb.tmp_data.get(obj.tbb.uid, None)
        return tmp_data is not None and tmp_data.is_ok()

    def execute(self, context: Context) -> set:
        """
        Preview the mesh.

        It also updates temporary data with this new preview.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        obj = get_selected_object(context)
        tmp_data = context.scene.tbb.tmp_data.get(obj.tbb.uid, None)
        clip = obj.tbb.settings.openfoam.clip
        io_settings = obj.tbb.settings.openfoam.import_settings
        collection = context.scene.collection

        if clip.type != "" and clip.scalar.name == "None":
            self.report({'WARNING'}, "Select a scalar to clip on. You may need to reload the file if none are shown")
            return {'FINISHED'}

        # Setup file_reader
        tmp_data.file_reader.decompose_polyhedra = io_settings.decompose_polyhedra
        tmp_data.file_reader.case_type = io_settings.case_type

        prw_time_point = obj.tbb.settings.preview_time_point

        # Generate mesh data
        try:
            tmp_data.update(prw_time_point, io_settings)
            vertices, faces, tmp_data.mesh = generate_mesh_data(tmp_data, clip=clip)
        except Exception:
            log.debug("Something went wrong building the mesh", exc_info=1)
            self.report({'WARNING'}, "Something went wrong building the mesh")
            return {'CANCELLED'}

        # Generate objects
        try:
            obj = generate_object_from_data(vertices, faces, "TBB_OpenFOAM_preview")
            blender_mesh = obj.data
            if collection.name not in [col.name for col in obj.users_collection]:
                collection.objects.link(obj)
        except Exception:
            log.debug("Something went generating the object", exc_info=1)
            self.report({'WARNING'}, "Something went generating the object")
            return {'CANCELLED'}

        # Import point data as vertex colors
        point_data = obj.tbb.settings.preview_point_data
        if point_data is not None and point_data != 'NONE':
            res = prepare_openfoam_point_data(obj.data, point_data, tmp_data)
            if len(res[0]) > 0:
                generate_vertex_colors(blender_mesh, *res)
                generate_preview_material(obj, res[0][0]["name"] if len(res[0]) > 0 else 'None')

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Mesh successfully built: checkout the viewport.")

        return {'FINISHED'}
