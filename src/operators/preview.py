from bpy.types import Operator

from .import_foam_file import load_openfoam_file, generate_preview_object

class TBB_OT_Preview(Operator):
    bl_idname="tbb.preview"
    bl_label="Preview"
    bl_description="Preview the current loaded file"

    def execute(self, context):
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        if settings.file_path == "":
            self.report({"ERROR"}, "Please import a file first.")
            return {"FINISHED"}

        # TODO: changing time point does not work if we do not load the file again... We would like to use the file_reader from TBB_temp_data.
        success, file_reader = load_openfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist.")
            return {"FINISHED"}

        if clip.type != "" and clip.scalars_props.scalars == "":
            self.report({"ERROR"}, "Please select a scalar to clip on. You may need to reload the file if none are shown.")
            return {"FINISHED"}
        
        # Read data at the choosen time step
        try:
            file_reader.set_active_time_point(settings["preview_time_step"])
        except ValueError as error:
            print("ERROR::TBB_OT_Preview: " + str(error))
            self.report({"ERROR"}, "The selected time step is not defined (" + str(settings["preview_time_step"]) + ").")
            return {"FINISHED"}
        
        data = file_reader.read()
        raw_mesh = data["internalMesh"]

        # Prepare the mesh for Blender
        if clip.type != "no_clip":
            try:
                preview_mesh = clip_mesh(clip, raw_mesh)
            except KeyError as error:
                print("ERROR::TBB_OT_Preview: " + str(error))
                self.report({"ERROR"}, "Can't clip on data named '" + str(clip.scalars_props.scalars) + "'. This field array can't be active.")
                # Update temporary data, please read the comment below.
                context.scene.tbb_temp_data.update(file_reader, settings["preview_time_step"], data, raw_mesh)
                return {"FINISHED"}

            preview_mesh = preview_mesh.extract_surface()
        else:
            preview_mesh = raw_mesh.extract_surface()

        # Update temporary data. We do not update it just after the reading of the file. Here is why.
        # This line will update the list of available scalars. If the choosen scalar is not available at
        # the selected time step, the program will automatically choose another scalar due to the update function
        # of the enum property. This is surely not what the user was expecting.
        context.scene.tbb_temp_data.update(file_reader, settings["preview_time_step"], data, raw_mesh)

        try:
            generate_preview_object(preview_mesh, context)
        except Exception as error:
            print("ERROR::TBB_OT_Preview: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        self.report({"INFO"}, "Mesh successfully built: checkout the viewport.")
        
        return {"FINISHED"}

def clip_mesh(clip, mesh):
    if clip.type == "scalar":
        scal = clip.scalars_props.scalars
        val = clip.scalars_props["value"]
        inv = clip.scalars_props.invert
        mesh.set_active_scalars(name=scal, preference="point")
        preview_mesh = mesh.clip_scalar(scalars=scal, invert=inv, value=val)
    
    return preview_mesh