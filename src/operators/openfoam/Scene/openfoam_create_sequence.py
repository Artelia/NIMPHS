# <pep8 compliant>
import bpy
from bpy.types import Context, Event

import time

from src.operators.utils import get_collection
from src.operators.shared.create_sequence import TBB_CreateSequence
from src.operators.openfoam.utils import generate_mesh_for_sequence, add_mesh_to_sequence


class TBB_OT_OpenfoamCreateSequence(TBB_CreateSequence):
    """
    Create an OpenFOAM sequence using the settings defined in the
    main panel of the module and the 'create sequence' panel.
    """
    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a sequence using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator. Calls 'super().poll(...)'.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context.scene.tbb.settings.openfoam, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Calls 'super().execute(...)'.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        return super().execute(context.scene.tbb.settings.openfoam, context, 'OpenFOAM')

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the OpenFOAM 'create mesh sequence' process.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        if event.type == "ESC":
            super().stop(context, cancelled=True)
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
                    super().stop(context)
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

                elapsed_time = "{:.4f}".format(time.time() - self.chrono_start)
                print("CreateSequence::OpenFOAM: " + elapsed_time + "s, time_point = " + str(self.current_time_point))

            else:
                super().stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            # Update the progress bar
            context.scene.tbb.progress_value = self.current_time_point / (self.end_time_point - self.start_time_point)
            context.scene.tbb.progress_value *= 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}
