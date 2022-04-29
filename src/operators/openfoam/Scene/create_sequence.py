# <pep8 compliant>
import bpy
from bpy.types import Operator, RenderSettings, Context, Event

import time

from ..utils import generate_mesh_for_sequence, add_mesh_to_sequence
from ...utils import get_collection, poll_create_sequence, stop_create_sequence, execute_create_sequence


class TBB_OT_OpenfoamCreateSequence(Operator):
    """
    Create a sequence using the settings defined in the main panel and the 'create sequence' panel.
    """

    bl_idname = "tbb.openfoam_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a sequence using the selected parameters. Press 'esc' to cancel"

    timer = None
    sequence_object_name = ""
    user_sequence_name = ""
    start_time_point = 0
    current_time_point = 0
    end_time_point = 0
    current_frame = 0

    chrono_start = 0

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator.

        :type context: Context
        :rtype: bool
        """

        settings = context.scene.tbb_openfoam_settings
        return poll_create_sequence(settings, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Its behaviour depends on the sequence type.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        settings = context.scene.tbb_openfoam_settings
        return execute_create_sequence(self, settings, context, 'OpenFOAM')

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'Create Mesh Sequence' process.

        :type context: Context
        :type event: Event
        :return: state of the operator
        :rtype: set
        """

        if event.type == "ESC":
            self.stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_point <= self.end_time_point:
                self.chrono_start = time.time()
                try:
                    mesh = generate_mesh_for_sequence(context, self.current_time_point, name=self.user_sequence_name)
                except Exception as error:
                    print("ERROR::TBB_OT_OpenfoamCreateSequence: " + str(error))
                    self.report({"ERROR"}, "An error occurred creating the sequence, (time_step = " +
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
                    get_collection("TBB_OpenFOAM", context).objects.link(obj)
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

    def stop(self, context: Context, cancelled: bool = False) -> None:
        """
        Stop the 'Create Mesh Sequence' process.

        :type context: Context
        :param cancelled: ask to report 'Create sequence cancelled', defaults to False
        :type cancelled: bool, optional
        """

        stop_create_sequence(self, context, cancelled)
