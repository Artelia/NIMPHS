import bpy
from bpy.types import Operator

from pyvista import OpenFOAMReader

from ..operators.import_foam_file import load_openfoam_file

def clip_mesh(clip, mesh):
    if clip.type == "scalar":
        scal = clip.scalars_props.scalars
        val = clip.scalars_props.value
        inv = clip.scalars_props.invert
        mesh.set_active_scalars(name=scal, preference="point")
        preview_mesh = mesh.clip_scalar(scalars=scal, invert=inv, value=val)
    
    return preview_mesh

class TBB_OT_Preview(Operator):
    bl_idname="tbb.preview"
    bl_label="Preview"
    bl_description="Preview the current loaded file"

    def execute(self, context):
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        if settings.file_path == "":
            self.report({"ERROR"}, "Please import a file first")
            return {"FINISHED"}

        success, file_reader = load_openfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}
        
        # Read data at the choosen time step
        try:
            file_reader.set_active_time_point(settings.preview_time_step)
        except ValueError as error:
            print(error)
            self.report({"ERROR"}, "The selected time step is not defined (" + str(settings.preview_time_step) + ")")
            return {"FINISHED"}
        
        data = file_reader.read()
        raw_mesh = data["internalMesh"]

        # Prepare the mesh for Blender
        if clip.type != "no_clip":
            preview_mesh = clip_mesh(clip, raw_mesh)
            preview_mesh = preview_mesh.extract_surface()
        else:
            preview_mesh = raw_mesh.extract_surface()

        preview_mesh = preview_mesh.triangulate()
        preview_mesh = preview_mesh.compute_normals(consistent_normals=False, split_vertices=True)

        # Prepare data to import the mesh into blender
        vertices = preview_mesh.points
        # TODO: This line can throw a value error
        faces = preview_mesh.faces.reshape((-1, 4))[:, 1:4]

        # Create the preview mesh (or write over it if it already exists)
        try:
            mesh = bpy.data.meshes["TBB_preview_mesh"]
            obj = bpy.data.objects["TBB_preview"]
        except KeyError as error:
            print(error)
            mesh = bpy.data.meshes.new("TBB_preview_mesh")
            obj = bpy.data.objects.new("TBB_preview", mesh)
            context.collection.objects.link(obj)
        
        context.view_layer.objects.active = obj
        mesh.clear_geometry()
        mesh.from_pydata(vertices, [], faces)

        self.report({"INFO"}, "Mesh successfully built: checkout the viewport")
        
        return {"FINISHED"}