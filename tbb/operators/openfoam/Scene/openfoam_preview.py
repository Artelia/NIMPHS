# <pep8 compliant>
from bpy.types import Operator, Context

import time
import logging
log = logging.getLogger(__name__)

from tbb.operators.utils import generate_object_from_data, generate_vertex_colors, get_temporary_data
from tbb.operators.openfoam.utils import (
    generate_mesh_data,
    prepare_openfoam_point_data,
    generate_preview_material)
from tbb.panels.utils import get_selected_object
from tbb.properties.openfoam.import_settings import TBB_OpenfoamImportSettings


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

        tmp_data = get_temporary_data(obj)
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
        tmp_data = get_temporary_data(obj)
        clip = obj.tbb.settings.openfoam.clip
        import_settings = obj.tbb.settings.openfoam.import_settings
        collection = context.scene.collection

        if clip.type != "" and clip.scalar.name == "None":
            self.report({'ERROR'}, "Select a scalar to clip on. You may need to reload the file if none are shown")
            return {'FINISHED'}

        # Setup file_reader
        file_reader = tmp_data.file_reader
        file_reader.decompose_polyhedra = import_settings.decompose_polyhedra
        file_reader.case_type = import_settings.case_type

        prw_time_point = obj.tbb.settings.openfoam.preview_time_point

        # Read data at the chosen time point
        try:
            file_reader.set_active_time_point(prw_time_point)
        except Exception:
            log.error("Error setting active time point", exc_info=1)
            self.report({'ERROR'}, f"Error setting active time point ({prw_time_point})")
            return {'FINISHED'}

        data = file_reader.read()
        raw_mesh = data["internalMesh"]

        try:
            vertices, faces, mesh = generate_mesh_data(
                file_reader, prw_time_point, triangulate=import_settings.triangulate, clip=clip, mesh=raw_mesh)
        except Exception:
            # Update temporary data, please read the comment below.
            tmp_data.update(file_reader, prw_time_point, data, raw_mesh)
            log.error("Something went wrong building the mesh", exc_info=1)
            self.report({'ERROR'}, "Something went wrong building the mesh")
            return {'FINISHED'}

        # Update temporary data. We do not update it just after the reading of the file. Here is why.
        # This line will update the list of available scalars. If the chosen scalar is not available at
        # the selected time point, the program will automatically choose another scalar due to the update function
        # of the enum property. This is surely not what the user was expecting.
        tmp_data.update(file_reader, prw_time_point, data, mesh)

        try:
            obj = generate_object_from_data(vertices, faces, "TBB_OpenFOAM_preview")
            blender_mesh = obj.data
            if collection.name not in [col.name for col in obj.users_collection]:
                collection.objects.link(obj)
        except Exception:
            log.error("Something went generating the object", exc_info=1)
            self.report({'ERROR'}, "Something went generating the object")
            return {'FINISHED'}

        settings = obj.tbb.settings
        point_data = settings.openfoam.preview_point_data
        res = prepare_openfoam_point_data(obj, settings, tmp_data, point_data)
        if len(res[0]) > 0:
            generate_vertex_colors(blender_mesh, *res)
            generate_preview_material(obj, res[0][0]["name"] if len(res[0]) > 0 else 'None')

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "Mesh successfully built: checkout the viewport.")

        return {'FINISHED'}
