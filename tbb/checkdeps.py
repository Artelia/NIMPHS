import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Check for Numba / CUDA
try:
    from numba import cuda
except BaseException:
    HAS_CUDA = False
    log.debug("CUDA unavailable")
else:
    if cuda.is_available():
        HAS_CUDA = True
        log.debug("CUDA available")
    else:
        HAS_CUDA = False
        log.debug("Numba/CUDA is installed but cannot find any device available")


# Check for multiprocessing
try:
    from multiprocessing import Process, RawArray
except BaseException:
    HAS_MULTIPROCESSING = False
    log.debug("Multiprocessing unavailable")
else:
    HAS_MULTIPROCESSING = True
    log.debug("Multiprocessing available")
