# <pep8 compliant>
from bpy.types import Scene
from bpy.app.handlers import persistent

import logging
log = logging.getLogger(__name__)

import time

from tbb.properties.utils.point_data import PointDataManager
from tbb.properties.utils.interpolation import InterpInfoMeshSequence
from tbb.operators.utils.object import OpenfoamObjectUtils, TelemacObjectUtils


@persistent
def update_openfoam_streaming_sequences(scene: Scene) -> None:
    """
    Update all OpenFOAM 'streaming sequence' objects of the scene.

    Args:
        scene (Scene): scene
    """

    frame = scene.frame_current
    if not scene.tbb.m_op_running:

        for obj in scene.objects:

            sequence = obj.tbb.settings.openfoam.s_sequence
            if obj.tbb.is_streaming_sequence and sequence.update:

                # Get file data
                try:
                    scene.tbb.file_data[obj.tbb.uid]
                except KeyError:
                    # Disable update
                    sequence.update = False
                    log.error(f"No file data available for {obj.name}. Disabling update.")
                    return

                time_point = frame - sequence.start
                if time_point >= 0 and time_point < sequence.length:

                    start = time.time()

                    try:
                        OpenfoamObjectUtils.update_streaming_sequence(scene, obj, time_point)
                    except Exception:
                        log.error(f"Error updating {obj.name}", exc_info=1)

                    log.info(f"Update {obj.name}: " + "{:.4f}".format(time.time() - start) + "s")


@persistent
def update_telemac_streaming_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'streaming sequence' objects of the scene.

    Args:
        scene (Scene): scene
    """

    # Check if a create sequence operator is running
    if scene.tbb.m_op_running:
        return

    for obj in scene.objects:
        # Check if current object is a streaming sequence
        if not obj.tbb.is_streaming_sequence:
            continue

        sequence = obj.tbb.settings.telemac.s_sequence
        interpolate = obj.tbb.settings.telemac.interpolate

        if sequence.update:

            # Get file data
            try:
                file_data = scene.tbb.file_data[obj.tbb.uid]
            except KeyError:
                # Disable update
                sequence.update = False
                log.error(f"No file data available for {obj.name}. Disabling update.")
                return

            # Compute limit (last time point to compute, takes interpolation into account)
            limit = sequence.start + sequence.length
            if interpolate.type != 'NONE':
                limit += (sequence.length - 1) * interpolate.time_steps

            if scene.frame_current >= sequence.start and scene.frame_current < limit:
                start = time.time()

                for child, id in zip(obj.children, range(len(obj.children))):
                    offset = id if file_data.is_3d() else 0
                    TelemacObjectUtils.update_streaming_sequence(obj, child, file_data, scene.frame_current, offset)

                log.info(obj.name + ", " + "{:.4f}".format(time.time() - start) + "s")


@persistent
def update_telemac_mesh_sequences(scene: Scene) -> None:
    """
    Update all TELEMAC 'mesh sequence' objects.

    Args:
        scene (Scene): scene
    """

    # Check if a create sequence operator is running
    if scene.tbb.m_op_running:
        return

    for obj in scene.objects:

        # Check if current object is a mesh sequence
        if not obj.tbb.is_mesh_sequence:
            continue

        point_data = obj.tbb.settings.point_data

        # Check if there are point data to import as vertex colors
        if point_data.import_data and PointDataManager(point_data.list).length() > 0:

            # Get file data
            try:
                file_data = scene.tbb.file_data[obj.tbb.uid]
            except KeyError:
                # Disable update
                point_data.import_data = False
                log.error(f"No file data available for {obj.name}. Disabling update.")
                return

            # Update children of the sequence object
            cumulated_time = 0.0

            for child, id in zip(obj.children, range(len(obj.children))):
                start = time.time()

                # Get interpolation time information
                time_info = InterpInfoMeshSequence(child, scene.frame_current)
                if time_info.has_data:
                    offset = id if file_data.is_3d() else 0
                    TelemacObjectUtils.update_mesh_sequence(child.data, file_data, offset, point_data, time_info)

                    cumulated_time += time.time() - start

            if cumulated_time > 0.0:
                log.info(obj.name + ", " + "{:.4f}".format(cumulated_time) + "s")
