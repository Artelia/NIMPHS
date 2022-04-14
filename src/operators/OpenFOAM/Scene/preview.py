# <pep8 compliant>
from bpy.types import Operator

import time

from ..utils import (
    clip_mesh,
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

        # Prepare the mesh for Blender
        if clip.type != "no_clip":
            try:
                preview_mesh = clip_mesh(clip, raw_mesh)
            except KeyError as error:
                print("ERROR::TBB_OT_OpenFOAMPreview: " + str(error))
                self.report({"ERROR"}, "Can't clip on data named '" +
                            str(clip.scalars_props.scalars) +
                            "'. This field array can't be active.")
                # Update temporary data, please read the comment below.
                tmp_data.update(file_reader, settings["preview_time_point"], data, raw_mesh)
                return {"FINISHED"}

            preview_mesh = preview_mesh.extract_surface()
        else:
            preview_mesh = raw_mesh.extract_surface()

        # Update temporary data. We do not update it just after the reading of the file. Here is why.
        # This line will update the list of available scalars. If the choosen scalar is not available at
        # the selected time step, the program will automatically choose another scalar due to the update function
        # of the enum property. This is surely not what the user was expecting.
        tmp_data.update(file_reader, settings["preview_time_point"], data, raw_mesh)

        try:
            scalars_to_preview = str(settings.preview_point_data.split("@")[0])  # Field array name
            blender_mesh, obj, preview_mesh = generate_preview_object(preview_mesh, context)
            blender_mesh = generate_vertex_colors(
                preview_mesh,
                blender_mesh,
                scalars_to_preview,
                settings["preview_time_point"])
            create_preview_material(obj, scalars_to_preview)
        except Exception as error:
            print("ERROR::TBB_OT_OpenFOAMPreview: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        print("Preview::openfoam: " + "{:.4f}".format(time.time() - start) + "s")
        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")

        return {"FINISHED"}
