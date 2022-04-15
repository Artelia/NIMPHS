# <pep8 compliant>
import bpy
from bpy.types import Mesh, Object, Scene, Context
from bpy.app.handlers import persistent
from rna_prop_ui import rna_idprop_ui_create

from pyvista import OpenFOAMReader, UnstructuredGrid
from pathlib import Path
import numpy as np
import time

from ...properties.OpenFOAM.Scene.settings import settings_dynamic_properties


def load_openopenfoam_file(file_path: str) -> tuple[bool, OpenFOAMReader]:
    file = Path(file_path)
    if not file.exists():
        return False, None

    # TODO: does this line can throw exceptions? How to manage errors here?
    file_reader = OpenFOAMReader(file_path)
    return True, file_reader


def generate_mesh(file_reader: OpenFOAMReader, time_point: int, clip=None,
                  mesh: UnstructuredGrid = None) -> tuple[np.array, np.array, UnstructuredGrid]:
    # Read data from the given OpenFoam file
    if mesh is None:
        file_reader.set_active_time_point(time_point)
        data = file_reader.read()
        mesh = data["internalMesh"]

    # Apply clip
    if clip is not None and clip.type == "scalar":
        name = clip.scalar.name.split("@")[0]
        mesh.set_active_scalars(name=name, preference="point")
        mesh.clip_scalar(inplace=True, scalars=name, invert=clip.scalar.invert, value=clip.scalar.value)
        mesh = mesh.extract_surface()
    else:
        mesh = mesh.extract_surface()

    mesh.triangulate(inplace=True)
    mesh.compute_normals(inplace=True, consistent_normals=False, split_vertices=True)

    vertices = np.array(mesh.points)
    faces = np.array(mesh.faces.reshape((-1, 4))[:, 1:4])

    return vertices, faces, mesh


def generate_preview_object(vertices: np.array, faces: np.array, context: Context,
                            name: str = "TBB_preview") -> tuple[Mesh, Object]:
    # Create the preview object (or write over it if it already exists)
    try:
        blender_mesh = bpy.data.meshes[name + "_mesh"]
        obj = bpy.data.objects[name]
    except KeyError as error:
        print("ERROR::generate_preview_object: " + str(error))
        blender_mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, blender_mesh)
        context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return blender_mesh, obj


def generate_preview_material(obj: Object, scalar: str, name: str = "TBB_preview_material") -> None:
    # Get the preview material
    try:
        material = bpy.data.materials[name]
    except KeyError as error:
        print("ERROR::generate_preview_material: " + str(error))
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True

    # Get node tree
    mat_node_tree = material.node_tree
    vertex_color_node = mat_node_tree.nodes.get(name + "_vertex_color")
    if vertex_color_node is None:
        # If the node does not exist, create it and link it to the shader
        vertex_color_node = mat_node_tree.nodes.new(type="ShaderNodeVertexColor")
        vertex_color_node.name = name + "_vertex_color"
        principled_bsdf_node = mat_node_tree.nodes.get("Principled BSDF")
        mat_node_tree.links.new(vertex_color_node.outputs[0], principled_bsdf_node.inputs[0])
        vertex_color_node.location = (-200, 250)

    # Update scalar to preview
    vertex_color_node.layer_name = scalar
    # Make sure it is the active material
    obj.active_material = material


def generate_mesh_for_sequence(context: Context, time_point: int, name: str = "TBB") -> Mesh:
    settings = context.scene.tbb_openfoam_settings

    # Read data from the given OpenFoam file
    file_reader = OpenFOAMReader(settings.file_path)
    vertices, faces, mesh = generate_mesh(file_reader, time_point, settings.clip)

    # Create mesh from python data
    blender_mesh = bpy.data.meshes.new(name + "_mesh")
    blender_mesh.from_pydata(vertices, [], faces)
    # Use fake user so Blender will save our mesh in the .blend file
    blender_mesh.use_fake_user = True

    # Import point data as vertex colors
    if settings.import_point_data:
        blender_mesh = generate_vertex_colors(mesh, blender_mesh, settings.list_point_data, time_point)

    return blender_mesh


def generate_vertex_colors(mesh: UnstructuredGrid, blender_mesh: Mesh, list_point_data: str, time_point: int) -> Mesh:
    # Prepare the mesh to loop over all its triangles
    if len(blender_mesh.loop_triangles) == 0:
        blender_mesh.calc_loop_triangles()
    vertex_ids = np.array([triangle.vertices for triangle in blender_mesh.loop_triangles]).flatten()

    # Filter field arrays (check if they exist)
    keys = list_point_data.split(";")
    filtered_keys = []
    for raw_key in keys:
        if raw_key != "":
            key = raw_key.split("@")[0]
            if key not in mesh.point_data.keys():
                print("WARNING::generate_vertex_colors: the field array named '" +
                      key + "' does not exist (time step = " + str(time_point) + ")")
            else:
                filtered_keys.append(key)

    for field_array in filtered_keys:
        # Get field array
        colors = mesh.get_array(name=field_array, preference="point")
        # Create new vertex colors array
        vertex_colors = blender_mesh.vertex_colors.new(name=field_array, do_init=True)
        # Normalize data
        colors = remap_array(colors)

        colors = 1.0 - colors
        # 1D scalars
        if len(colors.shape) == 1:
            # Copy values to the B and G color channels
            data = np.tile(np.array([colors[vertex_ids]]).transpose(), (1, 3))
        # 2D scalars
        if len(colors.shape) == 2:
            data = colors[vertex_ids]

        # Add a one for the 'alpha' color channel
        ones = np.ones((len(vertex_ids), 1))
        data = np.hstack((data, ones))

        data = data.flatten()
        vertex_colors.data.foreach_set("color", data)

    return blender_mesh


# Code taken from the Stop-motion-OBJ addon
# Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/stop_motion_obj.py
def add_mesh_to_sequence(seqObj: Object, blender_mesh: Mesh) -> int:
    blender_mesh.inMeshSequence = True
    mss = seqObj.mesh_sequence_settings
    # add the new mesh to meshNameArray
    newMeshNameElement = mss.meshNameArray.add()
    newMeshNameElement.key = blender_mesh.name_full
    newMeshNameElement.inMemory = True
    # increment numMeshes
    mss.numMeshes = mss.numMeshes + 1
    # increment numMeshesInMemory
    mss.numMeshesInMemory = mss.numMeshesInMemory + 1
    # set initialized to True
    mss.initialized = True
    # set loaded to True
    mss.loaded = True

    return mss.numMeshes - 1


@persistent
def update_sequence_on_frame_change(scene: Scene) -> None:
    frame = scene.frame_current

    for obj in scene.objects:
        if obj.tbb_openfoam_sequence.is_on_frame_change_sequence:
            if obj.tbb_openfoam_sequence.update_on_frame_change:
                settings = obj.tbb_openfoam_sequence
                time_point = frame - settings.frame_start

                if time_point >= 0 and time_point < settings.anim_length:
                    start = time.time()
                    update_sequence_mesh(obj, settings, time_point)
                    print("Update::" + settings.name + " : " + "{:.4f}".format(time.time() - start) + "s")


def update_sequence_mesh(obj: Object, settings, time_point: int) -> None:
    file_reader = OpenFOAMReader(settings.file_path)

    # Check if time point is ok
    if time_point >= file_reader.number_time_points:
        print("WARNING::update_sequence_mesh: time point '" + str(time_point) +
              "' does not exist. Available time points: " + str(file_reader.number_time_points))
        return

    vertices, faces, mesh = generate_mesh(file_reader, time_point, settings.clip)

    blender_mesh = obj.data
    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    # Import point data as vertex colors
    if settings.import_point_data:
        blender_mesh = generate_vertex_colors(mesh, blender_mesh, settings.list_point_data, time_point)


def update_properties_values(context: Context, file_reader: OpenFOAMReader) -> None:
    settings = context.scene.tbb_openfoam_settings

    # Settings
    max_time_step = file_reader.number_time_points
    update_settings_props(settings, max_time_step - 1)
    update_mesh_sequence_frame_settings(settings, context.scene, max_time_step)


def update_mesh_sequence_frame_settings(settings, scene: Scene, max_length: int) -> None:
    frame_start_prop = settings.get("frame_start")
    anim_length_prop = settings.get("anim_length")

    # Create the properties if they do not exist
    if frame_start_prop is None:
        rna_idprop_ui_create(
            settings,
            "frame_start",
            default=1,
            min=1,
            soft_min=1,
            max=250,
            soft_max=250,
            description="Starting point of the sequence"
        )
    else:
        prop = settings.id_properties_ui("frame_start")
        new_min = scene.frame_start
        new_max = scene.frame_end
        default = settings["frame_start"]
        if new_min > default or new_max < default:
            default = new_min
        prop.update(default=default, min=new_min, soft_min=new_min, max=new_max, soft_max=new_max)

    if anim_length_prop is None:
        rna_idprop_ui_create(
            settings,
            "anim_length",
            default=1,
            min=1,
            soft_min=1,
            max=max_length,
            soft_max=max_length,
            description="Length of the animation",
        )
    else:
        prop = settings.id_properties_ui("anim_length")
        new_max = max_length
        default = settings["anim_length"]
        if new_max < default:
            default = new_min
        prop.update(default=default, max=new_max, soft_max=new_max)


def update_settings_props(settings, new_max) -> None:
    for prop_id, prop_desc in settings_dynamic_properties:
        if settings.get(prop_id) is None:
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
        if new_max < default:
            default = 0
        prop.update(default=default, min=0, soft_min=0, max=new_max, soft_max=new_max)


def remap_array(input: np.array, out_min=0.0, out_max=1.0) -> np.array:
    in_min = np.min(input)
    in_max = np.max(input)

    if out_min < np.finfo(np.float).eps and out_max < np.finfo(np.float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
