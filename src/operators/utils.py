# <pep8 compliant>
from typing import Any
import bpy
from bpy.types import Collection, Mesh, Object, Context, RenderSettings
from rna_prop_ui import rna_idprop_ui_create

from ..properties.scene_settings import scene_settings_dynamic_props

import numpy as np


def get_collection(name: str, context: Context, link_to_scene: bool = True) -> Collection:
    """
    Get the collection named 'name'. If it does not exist, create it.

    :param name: name of the collection
    :type name: str
    :type context: Context
    :param link_to_scene: automatically the collection to the list of scene collections, defaults to True
    :type link_to_scene: bool
    :return: the collection
    :rtype: Collection
    """

    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name=name)
        if link_to_scene:
            context.scene.collection.children.link(collection)

    return collection


def generate_object_from_data(vertices: np.ndarray, faces: np.ndarray, name: str) -> tuple[Mesh, Object]:
    """
    Generate an object and its mesh using the given vertices and faces.

    :param vertices: vertices, must have the following shape: (n, 3)
    :type vertices: np.ndarray
    :param faces: faces, must have the following shape: (n, 3)
    :type faces: np.ndarray
    :param name: name of the preview object
    :type name: str
    :return: Blender mesh (of the generated object), generated object
    :rtype: tuple[Mesh, Object]
    """

    # Create the object (or write over it if it already exists)
    obj = bpy.data.objects.get(name)
    if obj is None:
        blender_mesh = bpy.data.meshes.get(name + "_mesh")
        if blender_mesh is None:
            blender_mesh = bpy.data.meshes.new(name + "_mesh")

        obj = bpy.data.objects.new(name, blender_mesh)
    else:
        blender_mesh = obj.data

    blender_mesh.clear_geometry()
    blender_mesh.from_pydata(vertices, [], faces)

    return blender_mesh, obj


def setup_openfoam_streaming_sequence_obj(obj: Object, context: Context) -> tuple[Any, int, Any]:
    """
    Setup settings for an OpenFOAM streaming sequence.

    :param obj: sequence object
    :type obj: Object
    :type context: Context
    :return: scene settings, number of time points, object settings
    :rtype: tuple[Any, int, Any]
    """

    settings = context.scene.tbb_openfoam_settings
    time_points = context.scene.tbb_openfoam_tmp_data.nb_time_points
    obj_settings = obj.tbb_openfoam_sequence

    # Set clip settings
    obj_settings.clip.type = settings.clip.type
    obj_settings.clip.scalar.list = settings.clip.scalar.list
    obj_settings.clip.scalar.value_ranges = settings.clip.scalar.value_ranges

    # Sometimes, the selected scalar may not correspond to ones available in the EnumProperty.
    # This happens when the selected scalar is not available at time point 0
    # (the EnumProperty only reads data at time point 0 to create the list of
    # available items)
    try:
        obj_settings.clip.scalar.name = settings.clip.scalar.name
    except TypeError as error:
        print("WARNING::setup_openfoam_streaming_sequence_object: " + str(error))

    obj_settings.clip.scalar.invert = settings.clip.scalar.invert
    # 'value' and 'vector_value' may not be defined, so use .get(prop, default_returned_value)
    obj_settings.clip.scalar["value"] = settings.clip.scalar.get("value", 0.5)
    obj_settings.clip.scalar["vector_value"] = settings.clip.scalar.get("vector_value", (0.5, 0.5, 0.5))

    return settings, time_points, obj_settings


def setup_telemac_streaming_sequence_obj(obj: Object, context: Context) -> tuple[Any, int, Any]:
    """
    Setup settings for a TELEMAC streaming sequence.

    :param obj: sequence object
    :type obj: Object
    :type context: Context
    :return: scene settings, number of time points, object settings
    :rtype: tuple[Any, int, Any]
    """

    settings = context.scene.tbb_telemac_settings
    time_points = context.scene.tbb_telemac_tmp_data.nb_time_points
    obj_settings = obj.tbb_telemac_sequence

    obj_settings.normalize = settings.normalize_sequence_obj

    return settings, time_points, obj_settings


def setup_streaming_sequence_object(obj: Object, context: Context, type: str):
    """
    Setup parameters of the given sequence object. Precise which streaming sequence you want to setup
    using the 'type' parameter.

    :param obj: sequence object
    :type obj: Object
    :type context: Context
    :param type: module name, enum in ['OpenFOAM', 'TELEMAC']
    :type type: str
    """

    if type == 'OpenFOAM':
        settings, time_points, obj_settings = setup_openfoam_streaming_sequence_obj(obj, context)
    if type == 'TELEMAC':
        settings, time_points, obj_settings = setup_telemac_streaming_sequence_obj(obj, context)

    # Setup common settings
    obj_settings.name = obj.name
    obj_settings.file_path = settings.file_path
    obj_settings.is_streaming_sequence = True
    obj_settings.update = True

    # Set the selected time frame
    obj_settings.frame_start = settings.frame_start     #
    obj_settings.max_length = time_points               # Order matters, check TBB_StreamingSequenceProperty class definition
    obj_settings.anim_length = settings["anim_length"]  #

    obj_settings.import_point_data = settings.import_point_data
    obj_settings.list_point_data = settings.list_point_data


def poll_create_sequence(settings, context: Context) -> bool:
    """
    Common poll function for OpenFOAM and TELEMAC 'Create sequence' operators.

    :param settings: settings
    :type context: Context
    :rtype: bool
    """
    result = None
    if settings.sequence_type == "mesh_sequence":
        result = not context.scene.tbb_create_sequence_is_running and settings["start_time_point"] < settings["end_time_point"]
    elif settings.sequence_type == "streaming_sequence":
        result = not context.scene.tbb_create_sequence_is_running
    else:  # Lock ui by default
        result = False

    return result


def execute_create_sequence(operator, settings, context: Context, type: str) -> set:
    """
    Common execute function for OpenFOAM and TELEMAC 'Create sequence' operators.

    :param operator: target operator
    :param settings: scene settings
    :type context: Context
    :param type: module name, enum in ['OpenFOAM', 'TELEMAC']
    :type type: str
    :return: state of the operator
    :rtype: set
    """

    wm = context.window_manager

    if settings.sequence_type == "mesh_sequence":
        # Create timer event
        operator.timer = wm.event_timer_add(time_step=1e-3, window=context.window)
        wm.modal_handler_add(operator)

        # Setup prograss bar
        context.scene.tbb_progress_label = "Create sequence"
        context.scene.tbb_progress_value = -1.0

        # Setup for creating the sequence
        operator.start_time_point = settings["start_time_point"]
        operator.current_time_point = settings["start_time_point"]
        operator.end_time_point = settings["end_time_point"]
        operator.current_frame = context.scene.frame_current
        operator.user_sequence_name = settings.sequence_name

        context.scene.tbb_create_sequence_is_running = True

        return {"RUNNING_MODAL"}

    elif settings.sequence_type == "streaming_sequence":
        # Warn the user when the selected start frame may be weird
        if settings.frame_start < context.scene.frame_start or settings.frame_start > context.scene.frame_end:
            operator.report({"WARNING"}, "Frame start is not in the selected time frame.")

        obj_name = settings.sequence_name + "_sequence"
        blender_mesh = bpy.data.meshes.new(name=settings.sequence_name + "_mesh")
        obj = bpy.data.objects.new(obj_name, blender_mesh)
        setup_streaming_sequence_object(obj, context, type)

        context.collection.objects.link(obj)

        # As mentionned here, lock the interface because the custom handler will alter data on frame change
        # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
        RenderSettings.use_lock_interface = True

        operator.report({"INFO"}, "Sequence successfully created")

        return {"FINISHED"}

    else:
        operator.report({"ERROR"}, "Unknown sequence type (type = " + str(settings.sequence_type) + ")")
        return {"FINISHED"}


def stop_create_sequence(operator, context: Context, cancelled: bool = False) -> None:
    """
    Common stop function for OpenFOAM and TELEMAC 'Create sequence' operators.

    :param operator: operator to stop
    :type context: Context
    :param cancelled: ask to report 'Create sequence cancelled', defaults to False
    :type cancelled: bool, optional
    """

    wm = context.window_manager
    wm.event_timer_remove(operator.timer)
    operator.timer = None
    context.scene.tbb_create_sequence_is_running = False
    context.scene.tbb_progress_value = -1.0
    if cancelled:
        operator.report({"INFO"}, "Create sequence cancelled")


def update_scene_settings_dynamic_props(settings, tmp_data) -> None:
    """
    Update 'dynamic' settings of the main panel. It adapts the max values of properties in function of the imported file.

    :param settings: scene settings
    :param tmp_data: temporary data
    """

    # This works because TBB_TelemacTemporaryData and TBB_OpenfoamTemporaryData have the same 'nb_time_points' attribute
    max_time_step = tmp_data.nb_time_points

    new_maxima = {
        "preview_time_point": max_time_step - 1,
        "start_time_point": max_time_step - 1,
        "end_time_point": max_time_step - 1,
        "anim_length": max_time_step,
    }
    update_dynamic_props(settings, new_maxima, scene_settings_dynamic_props)


def update_dynamic_props(settings, new_maxima, props) -> None:
    for prop_id, prop_desc in props:
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
        if new_maxima[prop_id] < default:
            default = 0
        prop.update(default=default, max=new_maxima[prop_id], soft_max=new_maxima[prop_id])


def remap_array(input: np.ndarray, out_min: float = 0.0, out_max: float = 1.0,
                in_min: float = -np.inf, in_max: float = np.inf) -> np.ndarray:
    """
    Remap values of the given array.

    :param input: input array to remap
    :type input: np.ndarray
    :param out_min: minimum value to output, defaults to 0.0
    :type out_min: float, optional
    :param out_max: maximum value to output, defaults to 1.0
    :type out_max: float, optional
    :param in_min: minimum value of the input, defaults to -1.0
    :type in_min: float, optional
    :param in_max: maximum value of the input, defaults to 1.0
    :type in_max: float, optional
    :return: output array
    :rtype: np.ndarray
    """

    if in_min == -np.inf or in_max == np.inf:
        in_min = np.min(input)
        in_max = np.max(input)

    if out_min < np.finfo(np.float).eps and out_max < np.finfo(np.float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
