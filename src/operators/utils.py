import bpy
from rna_prop_ui import rna_idprop_ui_create

from pyvista import OpenFOAMReader
from pathlib import Path

from ..properties.settings import settings_dynamic_properties

def load_openfoam_file(file_path):
    file = Path(file_path)
    if not file.exists():
        return False, None

    # TODO: does this line can throw exceptions? How to manage errors here?
    file_reader = OpenFOAMReader(file_path)
    return True, file_reader



def clip_mesh(clip, mesh):
    if clip.type == "scalar":
        scal = clip.scalars_props.scalars
        val = clip.scalars_props["value"]
        inv = clip.scalars_props.invert
        mesh.set_active_scalars(name=scal, preference="point")
        clipped_mesh = mesh.clip_scalar(scalars=scal, invert=inv, value=val)
    
    return clipped_mesh



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
    if clip.scalars_props.get("vector_value") == None:
        rna_idprop_ui_create(
            clip.scalars_props,
            "vector_value",
            default=(0.5, 0.5, 0.5),
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