# <pep8 compliant>
import bpy
from bpy.types import Context, Event, Object, Collection

import time

from ..utils import generate_mesh, normalize_objects, get_object_dimensions_from_mesh, set_new_shape_key
from ...shared.create_sequence import TBB_CreateSequence
from ...utils import get_collection, generate_object_from_data
from ....properties.telemac.temporary_data import TBB_TelemacTemporaryData
from ....properties.telemac.Object.telemac_object_settings import TBB_TelemacObjectSettings


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
            # If the 'Create TELEMAC Mesh sequence' process is not finished
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
                        objects = self.generate_base_objects(tmp_data, settings, name, collection)
                    except Exception as error:
                        print("ERROR::TBB_OT_TelemacCreateSequence: " + str(error))
                        self.report({"ERROR"}, "An error occurred creating the sequence")
                        super().stop(context)
                        return {"CANCELLED"}

                    # Create the sequence object
                    seq_obj = bpy.data.objects.new(name=name, object_data=None)

                    # Parent objects
                    for child in objects:
                        child.parent = seq_obj

                    self.sequence_object_name = seq_obj.name
                    collection.objects.link(seq_obj)

                # Other time points, update vertices
                else:
                    seq_obj = bpy.data.objects[name]
                    time_point = self.current_time_point

                    for obj, id in zip(seq_obj.children, range(len(seq_obj.children))):
                        if not tmp_data.is_3d:
                            type = obj.tbb.settings.telemac.z_name
                            vertices = generate_mesh(tmp_data, mesh_is_3d=False, time_point=time_point, type=type)
                        else:
                            vertices = generate_mesh(tmp_data, mesh_is_3d=True, offset=id, time_point=time_point)

                        set_new_shape_key(obj, vertices.flatten(), str(time_point), self.current_frame)

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

    def generate_base_objects(self, tmp_data: TBB_TelemacTemporaryData,
                              settings: TBB_TelemacObjectSettings, name: str, collection: Collection) -> list[Object]:
        """
        Generate base objects for the 'mesh sequence'.

        :param tmp_data: temporary data
        :type tmp_data: TBB_TelemacTemporaryData
        :param settings: object settings
        :type settings: TBB_TelemacObjectSettings
        :param name: name of the sequence object
        :type name: str
        :param collection: target collection for these new objects
        :type collection: Collection
        :return: list of generated objects
        :rtype: list[Object]
        """

        time_point = self.start_time_point
        objects = []
        if not tmp_data.is_3d:
            for type in ['BOTTOM', 'WATER_DEPTH']:
                # Generate object
                vertices = generate_mesh(tmp_data, mesh_is_3d=False, time_point=time_point, type=type)
                obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_" + type.lower())
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = type
                # Add 'Basis' shape key
                obj.shape_key_add(name="Basis", from_mix=False)

                # Add the object to the collection
                collection.objects.link(obj)
                objects.append(obj)
        else:
            for plane_id in range(tmp_data.nb_planes - 1, -1, -1):
                vertices = generate_mesh(tmp_data, mesh_is_3d=True, offset=plane_id, time_point=time_point)
                obj = generate_object_from_data(vertices, tmp_data.faces, name=name + "_plane_" + str(plane_id))
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = str(plane_id)
                # Add 'Basis' shape key
                obj.shape_key_add(name="Basis", from_mix=False)

                # Add the object to the collection
                collection.objects.link(obj)
                objects.append(obj)

        # Normalize if needed (option set by the user)
        if settings.normalize_sequence_obj:
            normalize_objects(objects, get_object_dimensions_from_mesh(objects[0]))

        return objects
