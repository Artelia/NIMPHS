import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# Numba / CUDA
try:
    from numba import cuda
except BaseException:
    HAS_CUDA = False
    log.debug("CUDA unavailable")
else:
    # Disable numba info logs
    numba_logger = logging.getLogger('numba')
    numba_logger.setLevel(logging.WARNING)

    if cuda.is_available():
        HAS_CUDA = True
        log.debug("CUDA available")
    else:
        HAS_CUDA = False
        log.debug("Numba/CUDA is installed but cannot find any device available")


# multiprocessing
try:
    from multiprocessing import Process, RawArray, Manager
except BaseException:
    HAS_MULTIPROCESSING = False
    log.debug("Multiprocessing unavailable")
else:
    HAS_MULTIPROCESSING = True
    log.debug("Multiprocessing available")


# OpenVDB
try:
    import pyopenvdb
except BaseException:
    HAS_PYOPENVDB = False
    log.debug("PyOpenVDB unavailable")
else:
    HAS_PYOPENVDB = True
    log.debug("PyOpenVDB available")
