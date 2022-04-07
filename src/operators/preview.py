import bpy
from bpy.types import Operator

from pyvista import OpenFOAMReader

class TBB_OT_Preview(Operator):
    bl_idname="tbb.preview"
    bl_label="Preview"
    bl_description="Preview the current loaded file"

    def execute(self, context):
        settings = context.scene.tbb_settings
        if settings.file_path == "":
            self.report({"ERROR"}, "Please import a file first")
            return {"FINISHED"}
        
        if bpy.types.TBB_PT_MainPanel.file_reader == None:
            self.report({"ERROR"}, "No data found: please reload the selected file")
            return {"FINISHED"}

        # Read data at the chosen time step
        try:
            bpy.types.TBB_PT_MainPanel.file_reader.set_active_time_point(settings.preview_time_step)
        except ValueError as error:
            self.report({"ERROR"}, "The selected time step is not defined (" + str(settings.preview_time_step) + ")")
            return {"FINISHED"}
            
        bpy.types.TBB_PT_MainPanel.openfoam_data = bpy.types.TBB_PT_MainPanel.file_reader.read()
        bpy.types.TBB_PT_MainPanel.openfoam_mesh = bpy.types.TBB_PT_MainPanel.openfoam_data["internalMesh"]

        # Prepare the mesh for Blender
        preview_mesh = bpy.types.TBB_PT_MainPanel.openfoam_mesh.extract_surface()
        preview_mesh = preview_mesh.triangulate()
        preview_mesh = preview_mesh.compute_normals(consistent_normals=False, split_vertices=True)

        # Prepare data to import the mesh into blender
        vertices = preview_mesh.points
        # TODO: This line can throw a value error
        faces = preview_mesh.faces.reshape((-1, 4))[:, 1:4]

        # Create the preview mesh
        mesh = bpy.data.meshes.new("TBB_review_mesh")  # add the new mesh
        obj = bpy.data.objects.new(mesh.name, mesh)
        col = context.collection
        col.objects.link(obj)
        context.view_layer.objects.active = obj

        mesh.from_pydata(vertices, [], faces)

        self.report({"INFO"}, "Mesh successfully built: checkout the viewport")
        
        return {"FINISHED"}