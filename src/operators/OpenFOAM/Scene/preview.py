# <pep8 compliant>
import bpy
from bpy.types import Operator

import time

from ..utils import (
    generate_mesh,
    get_clip_from_scene_clip,
    load_openopenfoam_file,
    generate_preview_object,
    generate_vertex_colors,
    create_preview_material
)


class TBB_OT_OpenFOAMPreview(Operator):
    bl_idname = "tbb.preview"
    bl_label = "Preview"
    bl_description = "Preview the current loaded file"

    def execute(self, context):
        settings = context.scene.tbb_openfoam_settings
        clip = context.scene.tbb_openfoam_clip
        tmp_data = context.scene.tbb_openfoam_tmp_data

        if settings.file_path == "":
            self.report({"ERROR"}, "Please import a file first.")
            return {"FINISHED"}

        if clip.type != "" and clip.scalars_props.scalars == "":
            self.report({"ERROR"}, "Please select a scalar to clip on. You may need to reload the file if none are shown.")
            return {"FINISHED"}

        start = time.time()
        # TODO: changing time point does not work if we do not load the file
        # again... We would like to use the file_reader from tbb_openfoam_tmp_data.
        success, file_reader = load_openopenfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist.")
            return {"FINISHED"}

        # Read data at the choosen time step
        try:
            file_reader.set_active_time_point(settings["preview_time_point"])
        except ValueError as error:
            print("ERROR::TBB_OT_OpenFOAMPreview: " + str(error))
            self.report({"ERROR"}, "The selected time step is not defined (" +
                        str(settings["preview_time_point"]) + ").")
            return {"FINISHED"}

        data = file_reader.read()
        raw_mesh = data["internalMesh"]

        try:
            clip_formatted = get_clip_from_scene_clip(clip)
            time_point = settings["preview_time_point"]
            vertices, faces, mesh = generate_mesh(file_reader, time_point, clip_formatted, raw_mesh)
        except Exception as error:
            print("ERROR::TBB_OT_OpenFOAMPreview: " + str(error))
            # Update temporary data, please read the comment below.
            tmp_data.update(file_reader, settings["preview_time_point"], data, raw_mesh)
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        # Update temporary data. We do not update it just after the reading of the file. Here is why.
        # This line will update the list of available scalars. If the choosen scalar is not available at
        # the selected time step, the program will automatically choose another scalar due to the update function
        # of the enum property. This is surely not what the user was expecting.
        tmp_data.update(file_reader, settings["preview_time_point"], data, raw_mesh)

        # Create the preview mesh (or write over it if it already exists)
        name = "Preview"
        try:
            blender_mesh = bpy.data.meshes[name + "_mesh"]
            obj = bpy.data.objects[name]
        except KeyError as error:
            print("ERROR::generate_preview_mesh: " + str(error))
            blender_mesh = bpy.data.meshes.new(name + "_mesh")
            obj = bpy.data.objects.new(name, blender_mesh)
            context.collection.objects.link(obj)

        context.view_layer.objects.active = obj
        blender_mesh.clear_geometry()
        blender_mesh.from_pydata(vertices, [], faces)

        scalars_to_preview = str(settings.preview_point_data.split("@")[0])
        blender_mesh = generate_vertex_colors(mesh, blender_mesh, scalars_to_preview, time_point)
        create_preview_material(obj, scalars_to_preview)

        print("Preview::openfoam: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
