import bpy
from bpy.types import Operator, RenderSettings

import time

from .utils import generate_mesh_for_sequence, add_mesh_to_sequence

class TBB_OT_CreateSequence(Operator):
    bl_idname="tbb.create_sequence"
    bl_label="Create sequence"
    bl_description="Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    timer = None
    sequence_object_name = ""
    user_sequence_name = ""
    start_time_step = 0
    current_time_step = 0
    end_time_step = 0
    current_frame = 0

    chrono_start = 0

    @classmethod
    def poll(cls, context):
        settings = context.scene.tbb_settings
        if settings.sequence_type == "mesh_sequence":
            return not settings.create_sequence_is_running and settings["start_time"] < settings["end_time"]
        elif settings.sequence_type == "on_frame_change":
            return not settings.create_sequence_is_running
        else: # Lock ui by default
            return False

    def execute(self, context):
        wm = context.window_manager
        settings = context.scene.tbb_settings
        clip = context.scene.tbb_clip

        if settings.sequence_type == "mesh_sequence":
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
            self.user_sequence_name = settings.sequence_name

            settings.create_sequence_is_running = True

            return {"RUNNING_MODAL"}

        elif settings.sequence_type == "on_frame_change":
            min_frame = context.scene.frame_start
            max_frame = context.scene.frame_end

            # Check if the selected time frame is ok
            if settings["frame_start"] < min_frame or settings["frame_start"] > max_frame:
                self.report({"ERROR"}, "Frame start is not in the selected time frame. See 'Output properties' > 'Frame range'")
                return {"FINISHED"}

            # Create an empty object
            obj_name = settings.sequence_name + "_sequence"
            blender_mesh = bpy.data.meshes.new(name=settings.sequence_name + "_mesh")
            obj = bpy.data.objects.new(obj_name, blender_mesh)
            obj.tbb_openfoam_sequence.is_on_frame_change_sequence = True
            obj.tbb_openfoam_sequence.update_on_frame_change = True
            obj.tbb_openfoam_sequence.file_path = settings.file_path
            obj.tbb_openfoam_sequence.name = obj_name

            # Set the selected time frame
            obj.tbb_openfoam_sequence.frame_start = settings["frame_start"]
            obj.tbb_openfoam_sequence.anim_length = settings["anim_length"]
            
            # Set clip settings
            obj.tbb_openfoam_sequence.clip_type = clip.type

            # Sometimes, the selected scalar may not correspond to ones available in the EnumProperty.
            # This happens when the selected scalar is not available at time point 0 (the EnumProperty only reads data at time point 0 to create the list of available items)
            try:
                obj.tbb_openfoam_sequence.clip_scalars = clip.scalars_props.scalars
            except TypeError as error:
                print("ERROR::TBB_OT_CreateSequence: " + str(error))
                self.report({"WARNING"}, "the selected scalar does not exist at time point 0 (selected from time point " + str(settings["preview_time_step"]) + ")")

            obj.tbb_openfoam_sequence.invert = clip.scalars_props.invert
            obj.tbb_openfoam_sequence.clip_value = clip.scalars_props["value"]
            obj.tbb_openfoam_sequence.clip_vactor_value = clip.scalars_props["vector_value"]
            obj.tbb_openfoam_sequence.import_point_data = settings.import_point_data
            obj.tbb_openfoam_sequence.list_point_data = settings.list_point_data

            context.collection.objects.link(obj)

            # As mentionned here, lock the interface because the custom handler will alter data on frame change
            # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
            RenderSettings.use_lock_interface = True

            self.report({"INFO"}, "Sequence properly set")

            return {"FINISHED"}

        else:
            self.report({"ERROR"}, "Unknown sequence type (type = " + str(settings.sequence_type) + ")")
            return {"FINISHED"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_step <= self.end_time_step:
                self.chrono_start = time.time() 
                try:
                    mesh = generate_mesh_for_sequence(context, self.current_time_step, name=self.user_sequence_name)
                except Exception as error:
                    print("ERROR::TBB_OT_CreateSequence: " + str(error))
                    self.report({"ERROR"}, "An error occured when creating the sequence, (time_step = " + str(self.current_time_step) + ")")
                    self.stop(context)
                    return {"CANCELLED"}

                # First time step, create the sequence object
                if self.current_time_step == self.start_time_step:
                    # Create the blender object (which will contain the sequence)
                    sequence_object = bpy.data.objects.new(self.user_sequence_name, mesh)
                    # The object created from the convert_to_mesh_sequence() method adds "_sequence" at the end of the name
                    self.sequence_object_name = sequence_object.name + "_sequence"
                    context.collection.objects.link(sequence_object)
                    # Convert it to a mesh sequence
                    context.view_layer.objects.active = sequence_object
                    bpy.ops.ms.convert_to_mesh_sequence()
                else:
                    # Add mesh to the sequence
                    sequence_object = bpy.data.objects[self.sequence_object_name]
                    context.scene.frame_set(frame=self.current_frame)

                    # Code taken from the Stop-motion-OBJ addon
                    # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/panels.py
                    # if the object doesn't have a 'curMeshIdx' fcurve, we can't add a mesh to it
                    # TODO: manage the case when there is no 'curMeshIdx'. We may throw an exception or something.
                    meshIdxCurve = next((curve for curve in sequence_object.animation_data.action.fcurves if 'curMeshIdx' in curve.data_path), None)

                    # add the mesh to the end of the sequence
                    meshIdx = add_mesh_to_sequence(sequence_object, mesh)

                    # add a new keyframe at this frame number for the new mesh
                    sequence_object.mesh_sequence_settings.curMeshIdx = meshIdx
                    sequence_object.keyframe_insert(data_path='mesh_sequence_settings.curMeshIdx', frame=context.scene.frame_current)

                    # make the interpolation constant for this keyframe
                    newKeyAtFrame = next((keyframe for keyframe in meshIdxCurve.keyframe_points if keyframe.co.x == context.scene.frame_current), None)
                    newKeyAtFrame.interpolation = 'CONSTANT'

                print("Create sequence (time_step = " + str(self.current_time_step) + "), elapsed time = " + "{:.4f}".format(time.time() - self.chrono_start) + "s")

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