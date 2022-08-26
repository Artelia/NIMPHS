# <pep8 compliant>
import bpy
from bpy.types import Object, Context, Mesh, Scene

import logging
log = logging.getLogger(__name__)

import time
import numpy as np
from typing import Union
from nimphs.properties.utils.point_data import PointDataManager
from nimphs.properties.telemac.file_data import TelemacFileData
from nimphs.properties.openfoam.file_data import OpenfoamFileData
from nimphs.operators.utils.mesh import OpenfoamMeshUtils, TelemacMeshUtils
from nimphs.properties.shared.point_data_settings import NIMPHS_PointDataSettings
from nimphs.operators.shared.create_streaming_sequence import NIMPHS_CreateStreamingSequence
from nimphs.properties.utils.interpolation import InterpInfo, InterpInfoStreamingSequence
from nimphs.operators.utils.vertex_color import OpenfoamVertexColorUtils, TelemacVertexColorUtils
from nimphs.operators.telemac.telemac_create_mesh_sequence import NIMPHS_OT_TelemacCreateMeshSequence
from nimphs.operators.openfoam.openfoam_create_mesh_sequence import NIMPHS_OT_OpenfoamCreateMeshSequence


class ObjectUtils():
    """Utility functions for generating objects for both modules."""

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
    def setup_streaming_sequence(cls, obj: Object, op: NIMPHS_CreateStreamingSequence, file_path: str) -> None:
        """
        Generate streaming sequence settings for all modules.

        Args:
            obj (Object): sequence object
            op (NIMPHS_CreateStreamingSequence): operator
            file_path (str): file path
        """

        # Get sequence settings
        if op.module == 'OpenFOAM':
            sequence = obj.nimphs.settings.openfoam.s_sequence
        if op.module == 'TELEMAC':
            sequence = obj.nimphs.settings.telemac.s_sequence

        # Setup common settings
        obj.nimphs.module = op.module
        obj.nimphs.is_streaming_sequence = True
        obj.nimphs.settings.file_path = file_path

        # Setup sequence settings
        sequence.start = op.start           # Order matters!
        sequence.max = op.max               # Check NIMPHS_StreamingSequenceProperty class definition.
        sequence.length = op.length         #
        sequence.update = True


class TelemacObjectUtils(ObjectUtils):
    """Utility functions for generating/updating objects for the TELEMAC module."""

    @classmethod
    def base(cls, file_data: TelemacFileData, name: str,
             point_data: Union[NIMPHS_PointDataSettings, str] = "") -> list[Object]:
        """
        Generate objects using settings defined by the user. This function generates objects and vertex colors.

        If the file is a 2D simulation, this will generate two objects ("Bottom" and "Water depth").
        If the file is a 3D simulation, this will generate one object per plane.

        Args:
            file_data (NIMPHS_TelemacFileData): file data
            name (str): name to give to the objects
            point_data (Union[NIMPHS_PointDataSettings, str], optional): point data settings. Defaults to "".

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
                obj.nimphs.settings.telemac.z_name = type

                if import_point_data:
                    data = TelemacVertexColorUtils.prepare(obj.data, point_data, file_data)
                    TelemacVertexColorUtils.generate(obj.data, data)

                objects.append(obj)
        else:
            for plane_id in range(file_data.nb_planes - 1, -1, -1):
                vertices = TelemacMeshUtils.vertices(file_data, offset=plane_id)
                obj = cls.generate(vertices, file_data.faces, name=f"{name}_plane_{plane_id}")
                # Save the name of the variable used for 'z-values' of the vertices
                obj.nimphs.settings.telemac.z_name = str(plane_id)

                if import_point_data:
                    data = TelemacVertexColorUtils.prepare(obj.data, point_data, file_data, offset=plane_id)
                    TelemacVertexColorUtils.generate(obj.data, data)

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
            file_data = TelemacFileData(obj.nimphs.settings.file_path)
        except BaseException:
            log.error("Unable to load file data")
            return None

        # Create sequence object
        sequence = bpy.data.objects.new(name=name, object_data=None)

        # Load file data
        sequence.nimphs.uid = str(time.time())
        file_data.copy(context.scene.nimphs.file_data[obj.nimphs.uid])
        context.scene.nimphs.file_data[sequence.nimphs.uid] = file_data

        try:
            children = cls.base(context.scene.nimphs.file_data[sequence.nimphs.uid], name)
        except BaseException:
            log.error("An error occurred generating the sequence object")
            return None

        for child in children:
            if shape_keys:
                # Add 'Basis' shape key
                child.shape_key_add(name="Basis", from_mix=False)
            # Add the object to the collection
            context.collection.objects.link(child)
            # Parent object
            child.parent = sequence

        return sequence

    @classmethod
    def add_shape_key(cls, obj: Object, vertices: np.ndarray, name: str, frame: int, end: bool) -> None:
        """
        Add a shape key to the object using the given vertices. It also set a keyframe with value = 1.0 at\
        the given frame and add keyframes at value = 0.0 around the frame (-1 and +1).

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
    def step_create_mesh_sequence(cls, context: Context, op: NIMPHS_OT_TelemacCreateMeshSequence) -> None:
        """
        Run one step of 'create mesh sequence' for the TELEMAC module.

        Args:
            context (Context): context
            op (NIMPHS_OT_TelemacCreateMeshSequence): operator
        """

        # First time point, create the sequence object
        if op.time_point == op.start:

            obj = cls.sequence(context, op.obj, op.name, shape_keys=True)
            obj.nimphs.module = 'TELEMAC'
            obj.nimphs.is_mesh_sequence = True
            obj.nimphs.settings.file_path = op.obj.nimphs.settings.file_path
            # Copy point data settings
            obj.nimphs.settings.point_data.import_data = op.point_data.import_data
            obj.nimphs.settings.point_data.list = op.point_data.list
            obj.nimphs.settings.point_data.remap_method = op.point_data.remap_method
            context.collection.objects.link(obj)

        # Other time points, update vertices
        else:
            obj = bpy.data.objects[op.name]
            file_data = context.scene.nimphs.file_data.get(obj.nimphs.uid, None)

            file_data.update_data(op.time_point)
            for child, id in zip(obj.children, range(len(obj.children))):
                if not file_data.is_3d():
                    type = child.nimphs.settings.telemac.z_name
                    vertices = TelemacMeshUtils.vertices(file_data, type=type)
                else:
                    vertices = TelemacMeshUtils.vertices(file_data, offset=id)

                cls.add_shape_key(child, vertices.flatten(), str(op.time_point), op.frame, op.time_point == op.end)

    @classmethod
    def update_mesh_sequence(cls, bmesh: Mesh, file_data: TelemacFileData, offset: int,
                             point_data: NIMPHS_PointDataSettings, time_info: InterpInfo) -> None:
        """
        Update the given TELEMAC 'mesh sequence' child object.

        Args:
            bmesh (Mesh): blender mesh
            file_data (NIMPHS_TelemacFileData): file data
            offset (int, optional): offset for data reading (id of the plane for 3D simulations). Defaults to 0.
            point_data (NIMPHS_PointDataSettings): point data
            time_info (InterpInfo): time information
        """

        # Remove existing vertex colors
        while bmesh.vertex_colors:
            bmesh.vertex_colors.remove(bmesh.vertex_colors[0])

        # Exit if no point data selected
        selected = PointDataManager(point_data.list)
        if selected.length() <= 0:
            return

        # Update point data
        data = TelemacVertexColorUtils.prepare_LI(bmesh, point_data, file_data, time_info, offset=offset)
        OpenfoamVertexColorUtils.generate(bmesh, data)

        # Update information of selected point data
        new = PointDataManager()
        for var in selected.names:
            new.append(data=file_data.vars.get(var))
        point_data.list = new.dumps()

    @classmethod
    def update_streaming_sequence(cls, obj: Object, child: Object, file_data: TelemacFileData,
                                  frame: int, offset: int) -> None:
        """
        Update the mesh of the given 'child' object from a TELEMAC 'streaming sequence' object.

        Args:
            obj (Object): sequence object
            child (Object): child object of the sequence
            file_data (NIMPHS_TelemacFileData): file data
            frame (int): frame
            offset (int): offset for data reading (id of the plane for 3D simulations).
        """

        # Get settings
        interpolate = obj.nimphs.settings.telemac.interpolate
        sequence = obj.nimphs.settings.telemac.s_sequence
        point_data = obj.nimphs.settings.point_data

        # Update mesh
        if interpolate.type == 'LINEAR':
            time_info = InterpInfoStreamingSequence(frame, sequence.start, interpolate.steps)
            vertices = TelemacMeshUtils.vertices_LI(child, file_data, time_info, offset)
        elif interpolate.type == 'NONE':
            time_point = frame - sequence.start
            file_data.update_data(time_point)
            vertices = TelemacMeshUtils.vertices(file_data, offset=offset, type=child.nimphs.settings.telemac.z_name)

        # Generate object
        child = cls.generate(vertices, file_data.faces, child.name)

        # Apply smooth shading
        if sequence.shade_smooth:
            child.data.polygons.foreach_set("use_smooth", [True] * len(child.data.polygons))

        # Update point data
        if point_data.import_data:

            # Exit if not point data selected
            selected = PointDataManager(point_data.list)
            if selected.length() <= 0:
                return

            # Remove old vertex colors
            while child.data.vertex_colors:
                child.data.vertex_colors.remove(child.data.vertex_colors[0])

            # Update vertex colors data
            if interpolate.type == 'LINEAR':
                data = TelemacVertexColorUtils.prepare_LI(child.data, point_data, file_data, time_info, offset=offset)
            elif interpolate.type == 'NONE':
                data = TelemacVertexColorUtils.prepare(child.data, point_data, file_data, offset=offset)

            TelemacVertexColorUtils.generate(child.data, data)

            # Update information of selected point data
            new = PointDataManager()
            for var in selected.names:
                new.append(data=file_data.vars.get(var))
            point_data.list = new.dumps()


class OpenfoamObjectUtils(ObjectUtils):
    """Utility functions for generating/updating meshes for the OpenFOAM module."""

    @classmethod
    def step_create_mesh_sequence(cls, context: Context, op: NIMPHS_OT_OpenfoamCreateMeshSequence) -> None:
        """
        Run one step of 'create mesh sequence' for the OpenFOAM module.

        Args:
            context (Context): context
            op (NIMPHS_OT_OpenfoamCreateMeshSequence): operator

        Raises:
            error: error on generating mesh for sequence
            ValueError: generated mesh is None
        """

        try:
            file_data = context.scene.nimphs.file_data["ops"]
            bmesh = cls.mesh_for_sequence(file_data, op)
        except BaseException as error:
            raise error

        # If the generated mesh is None, do not continue
        if bmesh is None:
            raise ValueError(f"Could not generate mesh at time point {op.time_point}, frame {op.frame}")

        # First time point, create the sequence object
        if op.time_point == op.start:
            # Create the blender object (which will contain the sequence)
            obj = bpy.data.objects.new(op.name, bmesh)
            # The object created from the convert_to_mesh_sequence() method adds
            # "_sequence" at the end of the name
            context.collection.objects.link(obj)
            # Convert it to a mesh sequence
            context.view_layer.objects.active = obj

            # TODO: is it possible not to call an operator and do it using functions?
            bpy.ops.ms.convert_to_mesh_sequence()
            # Remove '_sequence' at the end of the name
            obj = bpy.data.objects.get(f"{op.name}_sequence")
            obj.name = obj.name[:-len("_sequence")]
        else:
            # Add mesh to the sequence
            obj = bpy.data.objects[op.name]
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
    def mesh_for_sequence(cls, file_data: OpenfoamFileData,
                          op: NIMPHS_OT_OpenfoamCreateMeshSequence) -> Union[Mesh, None]:
        """
        Generate mesh data for the 'create mesh sequence' process.

        Args:
            file_data (NIMPHS_OpenfoamFileData): file data
            op (NIMPHS_OT_OpenfoamCreateMeshSequence): operator

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
            data = OpenfoamVertexColorUtils.prepare(bmesh, op.point_data, file_data)
            OpenfoamVertexColorUtils.generate(bmesh, data)

        return bmesh

    # Code taken from the Stop-motion-OBJ addon
    # Link: https://github.com/neverhood311/Stop-motion-OBJ/blob/rename-module-name/src/stop_motion_obj.py
    # Line: 1192
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

    @classmethod
    def streaming_sequence_obj(cls, context: Context, obj: Object, name: str) -> Object:
        """
        Generate the base object for an OpenFOAM 'streaming sequence'.

        Args:
            obj (Object): selected object
            name (str): name of the sequence

        Returns:
            Object: generated object
        """

        # Generate new file data
        try:
            file_data = OpenfoamFileData(
                obj.nimphs.settings.file_path,
                obj.nimphs.settings.openfoam.import_settings)
        except BaseException:
            log.error("Unable to load file data.")
            return None

        # Create the object
        bmesh = bpy.data.meshes.new(f"{name}_mesh")
        sequence = bpy.data.objects.new(name, bmesh)
        sequence.nimphs.uid = str(time.time())

        # Copy import settings from the selected object
        data = obj.nimphs.settings.openfoam.import_settings
        dest = sequence.nimphs.settings.openfoam.import_settings

        dest.case_type = data.case_type
        dest.triangulate = data.triangulate
        dest.skip_zero_time = data.skip_zero_time
        dest.decompose_polyhedra = data.decompose_polyhedra

        # Copy file data
        file_data.copy(context.scene.nimphs.file_data[obj.nimphs.uid])
        context.scene.nimphs.file_data[sequence.nimphs.uid] = file_data

        return sequence

    @classmethod
    def update_streaming_sequence(cls, scene: Scene, obj: Object, time_point: int) -> None:
        """
        Update the given OpenFOAM sequence object.

        Args:
            scene (Scene): scene
            obj (Object): sequence object
            time_point (int): time point
        """

        # Get data and settings
        io_settings = obj.nimphs.settings.openfoam.import_settings
        file_data = scene.nimphs.file_data[obj.nimphs.uid]

        # Check file data
        if file_data is None:
            return

        file_data.update_import_settings(io_settings)
        file_data.update_data(time_point)
        vertices, file_data.mesh = OpenfoamMeshUtils.vertices(file_data, clip=obj.nimphs.settings.openfoam.clip)
        faces = OpenfoamMeshUtils.faces(file_data.mesh)

        # Check mesh data
        if vertices is None or faces is None:
            return

        bmesh = obj.data
        bmesh.clear_geometry()
        bmesh.from_pydata(vertices, [], faces)

        # Shade smooth
        if obj.nimphs.settings.openfoam.s_sequence.shade_smooth:
            bmesh.polygons.foreach_set("use_smooth", [True] * len(bmesh.polygons))

        # Import point data as vertex colors
        point_data = obj.nimphs.settings.point_data
        if point_data.import_data and file_data.mesh is not None:

            # Exit if no point data selected
            selected = PointDataManager(point_data.list)
            if selected.length() <= 0:
                return

            data = OpenfoamVertexColorUtils.prepare(bmesh, point_data, file_data)
            OpenfoamVertexColorUtils.generate(bmesh, data)

            # Update information of selected point data
            new = PointDataManager()
            for var in selected.names:
                new.append(data=file_data.vars.get(var))
            point_data.list = new.dumps()
