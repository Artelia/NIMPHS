# <pep8 compliant>
from bpy.types import Object, Mesh

import logging
log = logging.getLogger(__name__)

import numpy as np


class InterpInfo():
    """Base class of utility classes to get interpolation information for sequence objects."""

    #: bool: Indicate if data has been successfully computed
    has_data: bool = False
    #: bool: Indicate the current time point is an existing time point
    exists: bool = True
    #: int: Frame at the "left" of the current time point
    left_frame: int = 0
    #: int: Number of time steps between each existing time point
    time_steps: int = 0
    #: int: Current frame
    frame: int = 0
    #: int: Next existing time point
    right: int = 0
    #: int: Previous existing time point
    left: int = 0

    def __init__(self) -> None:
        """Init method of the class."""

        self.has_data = False
        self.exists = True
        self.left_frame = 0
        self.time_steps = 0
        self.frame = 0
        self.right = 0
        self.left = 0

    def __str__(self) -> str:
        """
        Output this data structure as a string.

        Returns:
            str: output string
        """

        output = "Interpolation information:\n"
        output += "EXISTS: " + ("True\n" if self.exists else "False\n")
        output += "LEFT FRAME: " + str(self.left_frame) + "\n"
        output += "TIME STEPS: " + str(self.time_steps) + "\n"
        output += "FRAME: " + str(self.frame) + "\n"
        output += "RIGHT: " + str(self.right) + "\n"
        output += "LEFT: " + str(self.left) + "\n"
        return output


class InterpInfoStreamingSequence(InterpInfo):
    """Utility class to get interpolation information for 'Streaming Sequence' objects."""

    def __init__(self, frame: int, start: int, time_steps: int) -> None:
        """
        Init method of the class.

        Args:
            frame (int): current frame
            start (int): start frame of the sequence
            time_steps (int): number of time steps between each time point
        """

        self.compute(frame, start, time_steps)

    def compute(self, frame: int, start: int, time_steps: int) -> None:
        """
        Compute time information for interpolation of 'Streaming Sequence' objects.

        Args:
            frame (int): _description_
            start (int): _description_
            time_steps (int): _description_
        """

        time_point = frame - start
        self.has_data = True

        if time_steps == 0:
            # If it is an existing time
            self.exists = True
            self.left_frame = frame
            self.time_steps = 0
            self.frame = frame
            self.right = time_point
            self.left = time_point
        else:
            # If it is an interpolated time point
            info = self.scan(time_point, time_steps)

            self.exists = info[2]
            self.left_frame = start + (time_steps + 1) * info[0]
            self.time_steps = time_steps
            self.frame = frame
            self.right = info[1]
            self.left = info[0]

    def scan(self, time_point: int, time_steps: int) -> tuple[int, int, bool]:
        """
        Scan time information for interpolation of 'Streaming Sequence' objects.

        Args:
            time_point (int): current time point
            time_steps (int): number of time steps between each time point

        Returns:
            tuple[int, int, bool]: left time point, right time point, if left time point is an existing time point
        """

        modulo = time_point % (time_steps + 1)
        l_time_point = int((time_point - modulo) / (time_steps + 1))
        r_time_point = l_time_point + 1

        return l_time_point, r_time_point, modulo == 0


class InterpInfoMeshSequence(InterpInfo):
    """Utility class to get interpolation information for 'Mesh Sequence' objects."""

    def __init__(self, obj: Object, frame: int, threshold: float = 0.0001) -> None:
        """
        Init method of the class.

        Args:
            obj (Object): 'Mesh Sequence' object
            frame (int): current frame
            threshold (float, optional): shape_key value threshold. Defaults to 0.0001.
        """

        self.compute(obj, frame, threshold=threshold)

    def compute(self, obj: Object, frame: int, threshold: float = 0.0001) -> None:
        """
        Compute time information for interpolation of 'Mesh Sequence' objects.

        Args:
            obj (Object): sequence object
            frame (int): current frame
            threshold (float, optional): shape_key value threshold. Defaults to 0.0001.
        """

        # Get information from shape keys
        info = self.scan(obj.data, threshold=threshold)

        if info["frame_start"] <= frame <= info["frame_end"]:
            self.has_data = True

            if info["state"] == 'BASIS':
                self.exists = True
                self.left_frame = info["frame_start"]
                self.time_steps = 0
                self.frame = frame
                self.right = info["start_offset"] + 1
                self.left = info["start_offset"]

            elif info["state"] == 'EXISTING':
                self.exists = True
                self.left_frame = info["frames"][0]
                self.time_steps = 0
                self.frame = frame
                self.right = info["time_points"][0] + 1
                self.left = info["time_points"][0]

            elif info["state"] == 'INTERPOLATED':
                self.exists = False
                self.left_frame = info["frames"][0]
                self.time_steps = np.abs(info["frames"][0] - info["frames"][1]) - 1
                self.frame = frame
                self.right = info["time_points"][1]
                self.left = info["time_points"][0]

        else:
            self.has_data = False

    def scan(self, bmesh: Mesh, threshold: float = 0.0001) -> None:
        """
        Scan time information for interpolation of 'Mesh Sequence' objects.

        .. code-block:: text

            Example of output:

            * Mesh sequence: frame start = 12, anim length = 50.
            * Shape keys are linearly interpolated (2 time steps between each time point)
            * Current frame: 125

                Timeline
                Frames:     (12)⌄    (15)⌄                  (125)⌄                       (159)⌄
                                *  +  +  *  ...   *  +  +  *  +  +  *  +  +  *  ...  *  +  +  *
                Time points: (0)⌃     (1)⌃    (36)⌃    (37)⌃    (38)⌃    (39)⌃            (49)⌃

            Outputs:
            {
                "state": enum in ['BASIS', 'EXISTING', 'INTERPOLATED'] here 'INTERPOLATED',
                "start_offset": 0,
                "time_points": [37, 38],
                "ids": [123, 126],
                "frame_start": 12,
                "frame_end": 159
            }

        Args:
            bmesh (Mesh): mesh from which to get the information
            threshold (float, optional): threshold on the shape_key value. Defaults to 0.0001.
        """

        fcurves = bmesh.shape_keys.animation_data.action.fcurves
        start_offset = int(bmesh.shape_keys.key_blocks[1].name) - 1
        output = {
            "state": "",
            "start_offset": start_offset,
            "time_points": [],
            "frames": [],
            "frame_start": fcurves[0].keyframe_points[0].co[0],
            "frame_end": fcurves[-1].keyframe_points[-1].co[0]
        }

        # Get active shape_keys information
        # Note: range starts from 1 because there is one more shape_key ('Basis')
        for fcurve, key_id in zip(fcurves, range(1, len(fcurves) + 1, 1)):
            if bmesh.shape_keys.key_blocks[key_id].value > threshold:
                output["frames"].append(fcurve.keyframe_points[1].co[0])
                output["time_points"].append(key_id + start_offset)

        # Check more precise info on time points
        if len(output["time_points"]) == 0:
            # If there are no active shape_keys
            output["state"] = 'BASIS'

        elif len(output["time_points"]) == 1:
            if bmesh.shape_keys.key_blocks[output["time_points"][0] - start_offset].value != 1.0:
                # If the time point is not an existing time point (value is not 1.0 for the shape_key)

                if output["time_points"][0] == 1:
                    # Check if this shape_key is between time points 0 and 1
                    # First time point
                    output["state"] = 'INTERPOLATED'
                    output["time_points"].append(start_offset)
                    output["frames"].append(fcurves[0].keyframe_points[0].co[0])
                else:
                    # Last time point
                    output["state"] = 'INTERPOLATED'
                    output["time_points"].append(len(fcurves))
                    output["frames"].append(fcurves[-1].keyframe_points[-1].co[0])
            else:
                # This shape_key is on an existing time point
                output["state"] = 'EXISTING'

        elif len(output["time_points"]) == 2:
            # This shape_key represents an interpolated time point
            output["state"] = 'INTERPOLATED'

        # Make sure it is always sorted
        output["frames"].sort()
        output["time_points"].sort()

        return output
