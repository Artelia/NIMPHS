import bpy
from bpy.types import Operator

from pyvista import OpenFOAMReader

from .preview import clip_mesh

class TBB_OT_CreateSequence(Operator):
    bl_idname="tbb.create_sequence"
    bl_label="Create sequence"
    bl_description="Create a mesh sequence using the selected parameters"

    timer = None
    sequence_object_name = ""
    start_time_step = 0
    current_time_step = 0
    end_time_step = 0
    current_frame = 0

    @classmethod
    def poll(cls, context):
        return not context.scene.tbb_settings.create_sequence_is_running

    def execute(self, context):
        wm = context.window_manager
        settings = context.scene.tbb_settings
        # Create timer event
        self.timer = wm.event_timer_add(time_step=1e-3, window=context.window)
        wm.modal_handler_add(self)

        # Setup prograss bar
        context.scene.tbb_progress_label = "Create sequence"
        context.scene.tbb_progress_value = -1.0

        # Setup for creating the sequence
        self.start_time_step = settings["start_time"]
        self.current_time_step = settings["start_time"]
        self.end_time_step = settings["end_time"]
        self.current_frame = context.scene.frame_current

        settings.create_sequence_is_running = True

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_step <= self.end_time_step:
                mesh = generate_mesh_for_sequence(context, self.current_time_step)

                # First time step, create the sequence object
                if self.current_time_step == self.start_time_step:
                    # Create the blender object (which will contain the sequence)
                    sequence_object = bpy.data.objects.new("TBB", mesh)
                    self.sequence_object_name = sequence_object.name + "_sequence"
                    context.collection.objects.link(sequence_object)
                    # Convert it to a mesh sequence
                    context.view_layer.objects.active = sequence_object
                    bpy.ops.ms.convert_to_mesh_sequence()
                else:
                    # Add the mesh to the sequence
                    sequence_object = bpy.data.objects[self.sequence_object_name]
                    context.scene.frame_set(frame=self.current_frame)

                    # Code taken from the Stop-motion-OBJ addon
                    # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/panels.py
                    # if the object doesn't have a 'curMeshIdx' fcurve, we can't add a mesh to it
                    # TODO: manage the case when there is no 'curMeshIdx'. We may throw an exception or something.
                    meshIdxCurve = next((curve for curve in sequence_object.animation_data.action.fcurves if 'curMeshIdx' in curve.data_path), None)

                    # add the mesh to the end of the sequence
                    meshIdx = addMeshToSequence(sequence_object, mesh)

                    # add a new keyframe at this frame number for the new mesh
                    sequence_object.mesh_sequence_settings.curMeshIdx = meshIdx
                    sequence_object.keyframe_insert(data_path='mesh_sequence_settings.curMeshIdx', frame=context.scene.frame_current)

                    # make the interpolation constant for this keyframe
                    newKeyAtFrame = next((keyframe for keyframe in meshIdxCurve.keyframe_points if keyframe.co.x == context.scene.frame_current), None)
                    newKeyAtFrame.interpolation = 'CONSTANT'

            else:
                self.stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            context.scene.tbb_progress_value = self.current_time_step / (self.end_time_step - self.start_time_step) * 100
            self.current_time_step += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}
    
    def stop(self, context, cancelled=False):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        self.timer = None
        context.scene.tbb_settings.create_sequence_is_running = False
        context.scene.tbb_progress_value = -1.0
        if cancelled:
            self.report({"INFO"}, "Create sequence cancelled")

def generate_mesh_for_sequence(context, time_step, name="TBB"):
    settings = context.scene.tbb_settings
    clip = context.scene.tbb_clip

    file_reader = OpenFOAMReader(settings.file_path)
    file_reader.set_active_time_point(time_step)
    data = file_reader.read()
    raw_mesh = data["internalMesh"]
    
    # Prepare the mesh for Blender
    if clip.type != "no_clip":
        mesh = clip_mesh(clip, raw_mesh)
        mesh = mesh.extract_surface()
    else:
        mesh = raw_mesh.extract_surface()

    mesh = mesh.triangulate()
    mesh = mesh.compute_normals(consistent_normals=False, split_vertices=True)

    # Prepare data to create the mesh into blender
    vertices = mesh.points
    faces = mesh.faces.reshape((-1, 4))[:, 1:4]

    # Create mesh from python data
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(vertices, [], faces)
    # Use fake user so Blender will save our mesh in the .blend file
    mesh.use_fake_user = True

    return mesh

# Code taken from the Stop-motion-OBJ addon
# Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/stop_motion_obj.py
# 'mesh' is a Blender mesh
# TODO: write another version that accepts a list of vertices and triangles
#       and creates a new Blender mesh
def addMeshToSequence(seqObj, mesh):
    mesh.inMeshSequence = True

    mss = seqObj.mesh_sequence_settings

    # add the new mesh to meshNameArray
    newMeshNameElement = mss.meshNameArray.add()
    newMeshNameElement.key = mesh.name_full
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