import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty
from rna_prop_ui import rna_idprop_ui_create

from pyvista import OpenFOAMReader
from pathlib import Path

from ..properties.settings import settings_dynamic_properties
from ..properties.clip import update_scalar_value_prop

class TBB_OT_ImportFoamFile(Operator, ImportHelper):
    bl_idname="tbb.import_foam_file"
    bl_label="Import"
    bl_description="Import an OpenFoam file"

    filter_glob: StringProperty(
        default="*.foam", # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        success, file_reader = load_openfoam_file(self.filepath)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath

        # Update properties values
        update_properties_values(settings, clip, file_reader)

        # Update temp data
        context.scene.tbb_temp_data.update(file_reader, settings["preview_time_step"])

        # Generate the preview mesh. This step is not present in the reload operator because
        # the preview mesh may already be loaded. Moreover, this step takes a while on large meshes.
        try:
            preview_mesh = context.scene.tbb_temp_data.mesh_data.extract_surface()
            generate_preview_object(preview_mesh, context)
        except Exception as error:
            print("ERROR::TBB_OT_ImportFoamFile: " + str(error))
            self.report({"ERROR"}, "Something went wrong building the mesh")
            return {"FINISHED"}

        self.report({"INFO"}, "File successfully imported")

        return {"FINISHED"}

class TBB_OT_ReloadFoamFile(Operator):
    bl_idname="tbb.reload_foam_file"
    bl_label="Reload"
    bl_description="Reload the selected file"

    def execute(self, context):
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip
        if settings.file_path == "":
            self.report({"ERROR"}, "Please select a file first")
            return {"FINISHED"}

        success, file_reader = load_openfoam_file(settings.file_path)
        if not success:
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        # Update properties values
        update_properties_values(settings, clip, file_reader)

        # Update temp data
        context.scene.tbb_temp_data.update(file_reader, settings["preview_time_step"])

        self.report({"INFO"}, "Reload successfull")
        
        return {"FINISHED"}

def update_properties_values(settings, clip, file_reader):
    # Settings
    max_time_step =  file_reader.number_time_points - 1
    update_settings_props(settings, max_time_step)
    # Scalar value prop
    # TODO: find a better way to create this property
    if clip.scalars_props.get("value") == None:
        rna_idprop_ui_create(
            clip.scalars_props,
            "value",
            default=0.5,
            min=0.0,
            soft_min=0.0,
            max=1.0,
            soft_max=1.0,
            description="Set the clipping value"
        )

def update_settings_props(settings, new_max):
    for prop_id, prop_desc in settings_dynamic_properties:
        if settings.get(prop_id) == None:
            rna_idprop_ui_create(
                settings,
                prop_id,
                default=0,
                min=0,
                soft_min=0,
                max=0,
                soft_max=0,
                description=prop_desc
            )

        prop = settings.id_properties_ui(prop_id)
        default = settings[prop_id]
        if new_max < default: default = 0
        prop.update(default=default, min=0, soft_min=0, max=new_max, soft_max=new_max)

def load_openfoam_file(file_path):
    file = Path(file_path)
    if not file.exists():
        return False, None

    # TODO: does this line can throw exceptions? How to manage errors here?
    file_reader = OpenFOAMReader(file_path)
    return True, file_reader

# The preview_mesh should be some extracted surface
def generate_preview_object(preview_mesh, context, name="TBB_preview"):
    preview_mesh = preview_mesh.triangulate()
    preview_mesh = preview_mesh.compute_normals(consistent_normals=False, split_vertices=True)

    # Prepare data to import the mesh into blender
    vertices = preview_mesh.points
    # TODO: This line can throw a value error
    faces = preview_mesh.faces.reshape((-1, 4))[:, 1:4]

    # Create the preview mesh (or write over it if it already exists)
    try:
        mesh = bpy.data.meshes[name + "_mesh"]
        obj = bpy.data.objects[name]
    except KeyError as error:
        print("ERROR::generate_preview_mesh: " + str(error))
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)
    
    context.view_layer.objects.active = obj
    mesh.clear_geometry()
    mesh.from_pydata(vertices, [], faces)