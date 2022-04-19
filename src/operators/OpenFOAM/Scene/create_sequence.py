# <pep8 compliant>
from pydoc import cli
import bpy
from bpy.types import Operator, RenderSettings

import time

from ..utils import generate_mesh_for_sequence, add_mesh_to_sequence, generate_sequence_object


class TBB_OT_OpenFOAMCreateSequence(Operator):
    bl_idname = "tbb.create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    timer = None
    sequence_object_name = ""
    user_sequence_name = ""
    start_time_point = 0
    current_time_point = 0
    end_time_point = 0
    current_frame = 0

    chrono_start = 0

    @classmethod
    def poll(cls, context):
        settings = context.scene.tbb_openfoam_settings

        if settings.sequence_type == "mesh_sequence":
            return not settings.create_sequence_is_running and settings["start_time_point"] < settings["end_time_point"]
        elif settings.sequence_type == "on_frame_change":
            return not settings.create_sequence_is_running
        else:  # Lock ui by default
            return False

    def execute(self, context):
        wm = context.window_manager
        settings = context.scene.tbb_openfoam_settings
        clip = settings.clip
        tmp_data = context.scene.tbb_openfoam_tmp_data

        if settings.sequence_type == "mesh_sequence":
            # Create timer event
            self.timer = wm.event_timer_add(time_step=1e-3, window=context.window)
            wm.modal_handler_add(self)

            # Setup prograss bar
            context.scene.tbb_progress_label = "Create sequence"
            context.scene.tbb_progress_value = -1.0

            # Setup for creating the sequence
            self.start_time_point = settings["start_time_point"]
            self.current_time_point = settings["start_time_point"]
            self.end_time_point = settings["end_time_point"]
            self.current_frame = context.scene.frame_current
            self.user_sequence_name = settings.sequence_name

            settings.create_sequence_is_running = True

            return {"RUNNING_MODAL"}

        elif settings.sequence_type == "on_frame_change":
            # Check if the selected time frame is ok
            if settings.frame_start < context.scene.frame_start or settings.frame_start > context.scene.frame_end:
                self.report({"WARNING"},
                            "Frame start is not in the selected time frame. See 'Output properties' > 'Frame range'")

            obj = generate_sequence_object(self, settings, clip, tmp_data.file_reader.number_time_points)

            context.collection.objects.link(obj)

            # As mentionned here, lock the interface because the custom handler will alter data on frame change
            # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
            RenderSettings.use_lock_interface = True

            self.report({"INFO"}, "Sequence successfully created")

            return {"FINISHED"}

        else:
            self.report({"ERROR"}, "Unknown sequence type (type = " + str(settings.sequence_type) + ")")
            return {"FINISHED"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_point <= self.end_time_point:
                self.chrono_start = time.time()
                try:
                    mesh = generate_mesh_for_sequence(context, self.current_time_point, name=self.user_sequence_name)
                except Exception as error:
                    print("ERROR::TBB_OT_OpenFOAMCreateSequence: " + str(error))
                    self.report({"ERROR"}, "An error occured creating the sequence, (time_step = " +
                                str(self.current_time_point) + ")")
                    self.stop(context)
                    return {"CANCELLED"}

                # First time point, create the sequence object
                if self.current_time_point == self.start_time_point:
                    # Create the blender object (which will contain the sequence)
                    obj = bpy.data.objects.new(self.user_sequence_name, mesh)
                    # The object created from the convert_to_mesh_sequence() method adds
                    # "_sequence" at the end of the name
                    self.sequence_object_name = obj.name + "_sequence"
                    context.collection.objects.link(obj)
                    # Convert it to a mesh sequence
                    context.view_layer.objects.active = obj
                    bpy.ops.ms.convert_to_mesh_sequence()
                else:
                    # Add mesh to the sequence
                    obj = bpy.data.objects[self.sequence_object_name]
                    context.scene.frame_set(frame=self.current_frame)

                    # Code taken from the Stop-motion-OBJ addon
                    # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/panels.py
                    # if the object doesn't have a 'curMeshIdx' fcurve, we can't add a mesh to it
                    # TODO: manage the case when there is no 'curMeshIdx'. We may throw an exception or something.
                    meshIdxCurve = next(
                        (curve for curve in obj.animation_data.action.fcurves if 'curMeshIdx' in curve.data_path), None)

                    # add the mesh to the end of the sequence
                    meshIdx = add_mesh_to_sequence(obj, mesh)

                    # add a new keyframe at this frame number for the new mesh
                    obj.mesh_sequence_settings.curMeshIdx = meshIdx
                    obj.keyframe_insert(
                        data_path='mesh_sequence_settings.curMeshIdx',
                        frame=context.scene.frame_current)

                    # make the interpolation constant for this keyframe
                    newKeyAtFrame = next(
                        (keyframe for keyframe in meshIdxCurve.keyframe_points if keyframe.co.x == context.scene.frame_current), None)
                    newKeyAtFrame.interpolation = 'CONSTANT'

                print("CreateSequence::OpenFOAM: " + "{:.4f}".format(time.time() - self.chrono_start) + "s, time_point = "
                      + str(self.current_time_point))

            else:
                self.stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            context.scene.tbb_progress_value = self.current_time_point / \
                (self.end_time_point - self.start_time_point) * 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}

    def stop(self, context, cancelled=False):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        self.timer = None
        context.scene.tbb_openfoam_settings.create_sequence_is_running = False
        context.scene.tbb_progress_value = -1.0
        if cancelled:
            self.report({"INFO"}, "Create sequence cancelled")
