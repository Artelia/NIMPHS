# <pep8 compliant>
import logging
log = logging.getLogger(__name__)

import numpy as np


def remap_array(input: np.ndarray, out_min: float = 0.0, out_max: float = 1.0,
                in_min: float = -np.inf, in_max: float = np.inf) -> np.ndarray:
    """
    Remap values of the given array.

    Args:
        input (np.ndarray): input array to remap
        out_min (float, optional): minimum value to output. Defaults to 0.0.
        out_max (float, optional): maximum value to output. Defaults to 1.0.
        in_min (float, optional): minimum value of the input. Defaults to -np.inf.
        in_max (float, optional): maximum value of the input. Defaults to np.inf.

    Returns:
        np.ndarray: output array
    """

    if in_min == -np.inf or in_max == np.inf:
        in_min = np.min(input)
        in_max = np.max(input)

    if out_min < np.finfo(float).eps and out_max < np.finfo(float).eps:
        return np.zeros(shape=input.shape)
    elif out_min == 1.0 and out_max == 1.0:
        return np.ones(shape=input.shape)

    if in_max - in_min > np.finfo(float).eps:
        return out_min + (out_max - out_min) * ((input - in_min) / (in_max - in_min))
    else:
        return np.ones(shape=input.shape)
