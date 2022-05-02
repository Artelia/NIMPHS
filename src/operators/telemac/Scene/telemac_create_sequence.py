# <pep8 compliant>
import bpy
from bpy.types import Context, Event

import time
import numpy as np

from ..utils import generate_object, normalize_objects, get_object_dimensions_from_mesh, get_data_from_possible_var_names
from ...shared.create_sequence import TBB_CreateSequence
from ...utils import get_collection


class TBB_OT_TelemacCreateSequence(TBB_CreateSequence):
    """
    Create an OpenFOAM sequence using the settings defined in the
    main panel of the module and the 'create sequence' panel.
    """

    bl_idname = "tbb.telemac_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a mesh sequence using the selected parameters. Press 'esc' to cancel"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, locks the UI button of the operator. Calls 'super().poll(...)'.

        :type context: Context
        :rtype: bool
        """

        return super().poll(context.scene.tbb.settings.telemac, context)

    def execute(self, context: Context) -> set:
        """
        Main function of the operator. Calls 'super().execute(...)'.

        :type context: Context
        :return: state of the operator
        :rtype: set
        """

        return super().execute(context.scene.tbb.settings.telemac, context, 'TELEMAC')

    def modal(self, context: Context, event: Event) -> set:
        """
        Run one step of the 'Create TELEMAC Mesh sequence' process.

        :type context: Context
        :type event: Event
        :return: state of the operator
        :rtype: set
        """

        if event.type == "ESC":
            super().stop(context, cancelled=True)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self.current_time_point <= self.end_time_point:
                self.chrono_start = time.time()

                settings = context.scene.tbb.settings.telemac
                tmp_data = settings.tmp_data
                name = self.user_sequence_name + "_sequence"

                # First time point, create the sequence object
                if self.current_time_point == self.start_time_point:

                    # Get settings and data
                    collection = get_collection("TBB_TELEMAC", context)

                    try:
                        objects = []
                        for obj_type in ['BOTTOM', 'WATER_DEPTH']:
                            # Generate object
                            obj = generate_object(tmp_data, mesh_is_3d=False, time_point=self.start_time_point,
                                                  type=obj_type, name=name)
                            # Add 'Basis' shape key
                            obj.shape_key_add(name="Basis", from_mix=False)

                            # Add the object to the collection
                            collection.objects.link(obj)
                            objects.append(obj)

                        # Normalize if needed (option set by the user)
                        if settings.normalize_sequence_obj:
                            normalize_objects(objects, get_object_dimensions_from_mesh(objects[0]))

                    except Exception as error:
                        print("ERROR::TBB_OT_TelemacCreateSequence: " + str(error))
                        self.report({"ERROR"}, "An error occurred creating the sequence")
                        super().stop(context)
                        return {"CANCELLED"}

                    # Create the blender object (which will contain the sequence)
                    seq_obj = bpy.data.objects.new(name=name, object_data=None)

                    # Parent objects
                    for child in objects:
                        child.parent = seq_obj

                    self.sequence_object_name = obj.name
                    collection.objects.link(seq_obj)
                else:
                    seq_obj = bpy.data.objects[name]
                    for obj in seq_obj.children:
                        # Update geometry
                        type = obj.name.split("_")[-1].upper()
                        if type == 'BOTTOM':
                            z_values, var_name = get_data_from_possible_var_names(tmp_data, ['BOTTOM', 'FOND'],
                                                                                  self.current_time_point)
                        if type == 'DEPTH':
                            z_values, var_name = get_data_from_possible_var_names(
                                tmp_data, ["WATER DEPTH", "HAUTEUR D'EAU", "FREE SURFACE", "SURFACE LIBRE"], self.current_time_point)

                            # Compute 'FREE SURFACE' from 'WATER_DEPTH' and 'BOTTOM'
                            if var_name in ["WATER DEPTH", "HAUTEUR D'EAU"]:
                                bottom, var_name = get_data_from_possible_var_names(
                                    tmp_data, ["BOTTOM", "FOND"], self.current_time_point)
                                z_values += bottom

                        vertices = np.hstack((tmp_data.vertices, z_values)).flatten()
                        obj.data.vertices.foreach_set("co", vertices)

                        # Add a shape key
                        block = obj.shape_key_add(name=str(self.current_time_point), from_mix=False)
                        block.value = 1.0
                        # Keyframe the new shape key
                        block.keyframe_insert("value", frame=self.current_frame, index=-1)
                        block.value = 0.0
                        block.keyframe_insert("value", frame=self.current_frame - 1, index=-1)
                        block.keyframe_insert("value", frame=self.current_frame + 1, index=-1)

                elapsed_time = "{:.4f}".format(time.time() - self.chrono_start)
                print("CreateSequence::TELEMAC: " + elapsed_time + "s, time_point = " + str(self.current_time_point))

            else:
                super().stop(context)
                self.report({"INFO"}, "Create sequence finished")
                return {"FINISHED"}

            # Update the progress bar
            context.scene.tbb_progress_value = self.current_time_point / (self.end_time_point - self.start_time_point)
            context.scene.tbb_progress_value *= 100
            self.current_time_point += 1
            self.current_frame += 1

        return {"PASS_THROUGH"}
