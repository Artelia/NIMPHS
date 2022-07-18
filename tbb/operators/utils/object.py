# <pep8 compliant>
import bpy
from bpy.types import Object, Context, Mesh

import logging
log = logging.getLogger(__name__)

import time
import numpy as np
from typing import Union
from tbb.operators.utils.mesh import OpenfoamMeshUtils, TelemacMeshUtils
from tbb.properties.telemac.file_data import TBB_TelemacFileData
from tbb.properties.openfoam.file_data import TBB_OpenfoamFileData
from tbb.operators.utils.vertex_colors import TelemacVertexColorsUtils
from tbb.properties.shared.point_data_settings import TBB_PointDataSettings
from tbb.operators.shared.create_streaming_sequence import TBB_CreateStreamingSequence
from tbb.operators.telemac.Scene.telemac_create_mesh_sequence import TBB_OT_TelemacCreateMeshSequence
from tbb.operators.openfoam.Scene.openfoam_create_mesh_sequence import TBB_OT_OpenfoamCreateMeshSequence


class ObjectUtils():

    @classmethod
    def generate(cls, vertices: np.ndarray, faces: np.ndarray, name: str, new: bool = False) -> Object:
        """
        Generate an object and its mesh using the given vertices and faces.

        If it already exists, clear object data and use the given data as new data.

        Args:
            vertices (np.ndarray): vertices, must have the following shape: (n, 3)
            faces (np.ndarray): faces, must have the following shape: (n, 3)
            name (str): name of the object
            new (bool): force to generate a new object

        Returns:
            Object: generated object
        """

        obj = bpy.data.objects.get(name) if not new else None
        if obj is None:
            bmesh = bpy.data.meshes.get(name + "_mesh") if not new else None
            if bmesh is None:
                bmesh = bpy.data.meshes.new(name + "_mesh")

            obj = bpy.data.objects.new(name, bmesh)
        else:
            bmesh = obj.data

        obj.shape_key_clear()
        bmesh.clear_geometry()
        bmesh.from_pydata(vertices, [], faces)

        return obj

    @classmethod
    def setup_streaming_sequence(cls, obj: Object, op: TBB_CreateStreamingSequence, file_path: str) -> None:
        """
        Generate streaming sequence settings for all modules.

        Args:
            obj (Object): sequence object
            op (TBB_CreateStreamingSequence): operator
            file_path (str): file path
        """

        # Get sequence settings
        if op.module == 'OpenFOAM':
            sequence = obj.tbb.settings.openfoam.s_sequence
        if op.module == 'TELEMAC':
            sequence = obj.tbb.settings.telemac.s_sequence

        # Setup common settings
        obj.tbb.module = op.module
        obj.tbb.is_streaming_sequence = True
        obj.tbb.settings.file_path = file_path

        # Setup sequence settings
        sequence.start = op.start           # Order matters!
        sequence.max = op.max               # Check TBB_StreamingSequenceProperty class definition.
        sequence.length = op.length         #
        sequence.update = True


class TelemacObjectUtils(ObjectUtils):

    @classmethod
    def base(cls, file_data: TBB_TelemacFileData, name: str,
             point_data: Union[TBB_PointDataSettings, str] = "") -> list[Object]:
        """
        Generate objects using settings defined by the user. This function generates objects and vertex colors.

        If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth").
        If the file is a 3D simulation, this will generate one object per plane.

        Args:
            file_data (TBB_TelemacFileData): file data
            name (str): name to give to the objects
            point_data (Union[TBB_PointDataSettings, str], optional): point data settings. Defaults to "".

        Returns:
            list[Object]: generated objects
        """

        # Check if we need to import point data
        if isinstance(point_data, str):
            import_point_data = point_data != ""
        else:
            import_point_data = point_data.import_data

        objects = []
        if not file_data.is_3d():

            for type in ['BOTTOM', 'WATER_DEPTH']:

                vertices = TelemacMeshUtils.vertices(file_data, type=type)
                obj = cls.generate(vertices, file_data.faces, name=f"{name}_{type.lower()}")
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = type

                if import_point_data:
                    data = TelemacVertexColorsUtils.prepare(obj.data, point_data, file_data)
                    TelemacVertexColorsUtils.generate(obj.data, data)

                objects.append(obj)
        else:
            for plane_id in range(file_data.nb_planes - 1, -1, -1):
                vertices = TelemacMeshUtils.vertices(file_data, offset=plane_id)
                obj = cls.generate(vertices, file_data.faces, name=f"{name}_plane_{plane_id}")
                # Save the name of the variable used for 'z-values' of the vertices
                obj.tbb.settings.telemac.z_name = str(plane_id)

                if import_point_data:
                    data = TelemacVertexColorsUtils.prepare(obj.data, point_data, file_data, offset=plane_id)
                    TelemacVertexColorsUtils.generate(obj.data, data)

                objects.append(obj)

        return objects

    @classmethod
    def sequence(cls, context: Context, obj: Object, name: str, shape_keys: bool = False) -> Union[Object, None]:
        """
        Generate base object for a TELEMAC sequence.

        Args:
            context (Context): context
            obj (Object): source object to copy data
            name (str): name to give to the sequence
            shape_keys (bool, optional): indicate whether to generate the 'Basis' shape key. Defaults to False.

        Returns:
            Union[Object, None]: generated sequence object
        """

        try:
            file_data = TBB_TelemacFileData(obj.tbb.settings.file_path)
        except BaseException:
            log.error("Unable to load file data")
            return None

        # Create sequence object
        sequence = bpy.data.objects.new(name=f"{name}_sequence", object_data=None)

        # Load file data
        sequence.tbb.uid = str(time.time())
        file_data.copy(context.scene.tbb.file_data[obj.tbb.uid])
        context.scene.tbb.file_data[sequence.tbb.uid] = file_data

        try:
            children = cls.base(context.scene.tbb.file_data[sequence.tbb.uid], f"{name}_sequence")
        except BaseException:
            log.error("An error occurred generating the sequence object")
            return None

        for child in children:
            if shape_keys:
                # Add 'Basis' shape key
                child.shape_key_add(name="Basis", from_mix=False)
            # Add the object to the collection
            context.scene.collection.objects.link(child)
            # Parent object
            child.parent = sequence

        return sequence

    @classmethod
    def add_shape_key(cls, obj: Object, vertices: np.ndarray, name: str, frame: int, end: bool) -> None:
        """
        Add a shape key to the object using the given vertices. It also set a keyframe with value = 1.0 at the given frame\
        and add keyframes at value = 0.0 around the frame (-1 and +1).

        Args:
            obj (Object): object to receive the new shape key
            vertices (np.ndarray): new vertices values
            name (str): name of the shape key
            frame (int): the frame on which the keyframe is inserted
            end (bool): indicate if this the shape key to add is the last one. Defaults to False.
        """

        obj.data.vertices.foreach_set("co", vertices.flatten())

        # Add a shape key
        block = obj.shape_key_add(name=name, from_mix=False)
        block.value = 1.0
        # Keyframe the new shape key
        block.keyframe_insert("value", frame=frame, index=-1)
        block.value = 0.0
        block.keyframe_insert("value", frame=frame - 1, index=-1)
        if not end:
            block.keyframe_insert("value", frame=frame + 1, index=-1)

    @classmethod
    def step_create_mesh_sequence(cls, context: Context, op: TBB_OT_TelemacCreateMeshSequence) -> None:
        """
        Run one step of 'create mesh sequence' for the TELEMAC module.

        Args:
            context (Context): context
            op (TBB_OT_TelemacCreateMeshSequence): operator
        """

        # First time point, create the sequence object
        if op.time_point == op.start:

            obj = cls.sequence(context, op.obj, op.name, op.start, shape_keys=True)
            obj.tbb.module = 'TELEMAC'
            obj.tbb.is_mesh_sequence = True
            obj.tbb.settings.file_path = op.obj.tbb.settings.file_path
            # Copy point data settings
            obj.tbb.settings.point_data.import_data = op.point_data.import_data
            obj.tbb.settings.point_data.list = op.point_data.list
            obj.tbb.settings.point_data.remap_method = op.point_data.remap_method
            context.scene.collection.objects.link(obj)

        # Other time points, update vertices
        else:
            obj = bpy.data.objects[f"{op.name}_sequence"]
            file_data = context.scene.tbb.file_data.get(obj.tbb.uid, None)

            file_data.update_data(op.time_point)
            for child, id in zip(obj.children, range(len(obj.children))):
                if not file_data.is_3d():
                    type = child.tbb.settings.telemac.z_name
                    vertices = TelemacMeshUtils.vertices(file_data, type=type)
                else:
                    vertices = TelemacMeshUtils.vertices(file_data, offset=id)

                cls.add_shape_key(child, vertices.flatten(), str(op.time_point), op.frame, op.time_point == op.end)


class OpenfoamObjectUtils():

    @classmethod
    def step_create_mesh_sequence(cls, context: Context, op: TBB_OT_OpenfoamCreateMeshSequence) -> None:
        """
        Run one step of 'create mesh sequence' for the OpenFOAM module.

        Args:
            context (Context): context
            op (TBB_OT_OpenfoamCreateMeshSequence): operator

        Raises:
            error: error on generating mesh for sequence
            ValueError: generated mesh is None
        """

        try:
            file_data = context.scene.tbb.file_data["ops"]
            bmesh = cls. generate_mesh_for_sequence(file_data, op)
        except Exception as error:
            raise error

        # If the generated mesh is None, do not continue
        if bmesh is None:
            raise ValueError(f"Generated mesh is None at time point {op.time_point}, frame {op.frame}")

        # First time point, create the sequence object
        if op.time_point == op.start:
            # Create the blender object (which will contain the sequence)
            obj = bpy.data.objects.new(op.name, bmesh)
            # The object created from the convert_to_mesh_sequence() method adds
            # "_sequence" at the end of the name
            context.scene.collection.objects.link(obj)
            # Convert it to a mesh sequence
            context.view_layer.objects.active = obj

            # TODO: is it possible not to call an operator and do it using functions?
            bpy.ops.ms.convert_to_mesh_sequence()
        else:
            # Add mesh to the sequence
            obj = bpy.data.objects[op.name + "_sequence"]
            context.scene.frame_set(frame=op.frame)

            # Code taken from the Stop-motion-OBJ addon
            # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/version-2.2/src/panels.py
            # if the object doesn't have a 'curMeshIdx' fcurve, we can't add a mesh to it
            # TODO: manage the case when there is no 'curMeshIdx'. We may throw an exception or something.
            curve = next(
                (curve for curve in obj.animation_data.action.fcurves if 'curKeyframeMeshIdx' in curve.data_path),
                None
            )

            # add the mesh to the end of the sequence
            meshIdx = cls.add_mesh_to_sequence(obj, bmesh)

            # add a new keyframe at this frame number for the new mesh
            obj.mesh_sequence_settings.curKeyframeMeshIdx = meshIdx
            obj.keyframe_insert(data_path='mesh_sequence_settings.curKeyframeMeshIdx', frame=op.frame)

            # make the interpolation constant for this keyframe
            newKey = next((keyframe for keyframe in curve.keyframe_points if keyframe.co.x == op.frame), None)
            newKey.interpolation = 'CONSTANT'

    @classmethod
    def mesh_for_sequence(cls, file_data: TBB_OpenfoamFileData,
                          op: TBB_OT_OpenfoamCreateMeshSequence) -> Union[Mesh, None]:
        """
        Generate mesh data for the 'create mesh sequence' process.

        Args:
            file_data (TBB_OpenfoamFileData): file data
            op (TBB_OT_OpenfoamCreateMeshSequence): operator

        Returns:
            Union[Mesh, None]: generated mesh
        """

        # Generate mesh data
        file_data.update_import_settings(op.import_settings)
        file_data.update_data(op.time_point)
        vertices, file_data.mesh = OpenfoamMeshUtils.vertices(file_data, clip=op.clip)
        faces = OpenfoamMeshUtils.faces(file_data.mesh)
        if file_data.mesh is None:
            return None

        # Create mesh from python data
        bmesh = bpy.data.meshes.new(f"{op.name}_sequence_mesh")
        bmesh.from_pydata(vertices, [], faces)
        # Use fake user so Blender will save our mesh in the .blend file
        bmesh.use_fake_user = True

        # Import point data as vertex colors
        if op.point_data.import_data:
            res = prepare_openfoam_point_data(bmesh, op.point_data, file_data)
            generate_vertex_colors(bmesh, *res)

        return bmesh

    # Code taken from the Stop-motion-OBJ addon
    # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/stop_motion_obj.py
    @classmethod
    def add_mesh_to_sequence(cls, obj: Object, bmesh: Mesh) -> int:
        """
        Add a mesh to an OpenFOAM 'mesh sequence'.

        Args:
            obj (Object): sequence object
            bmesh (Mesh): mesh to add to the sequence

        Returns:
            int: mesh id in the sequence
        """

        bmesh.inMeshSequence = True
        mss = obj.mesh_sequence_settings
        # add the new mesh to meshNameArray
        newMeshNameElement = mss.meshNameArray.add()
        newMeshNameElement.key = bmesh.name_full
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
