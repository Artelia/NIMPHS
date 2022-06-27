# <pep8 compliant>
from bpy.types import Context

import logging
log = logging.getLogger(__name__)


def update_start(self, _context: Context) -> None:  # noqa D417
    """
    Update time point (make sure the user can't selected an undifined time point).

    Args:
        _context (Context):
    """

    if self.start > self.max - 1:
        self.start = self.max - 1
    elif self.start < 0:
        self.start = 0


def update_end(self, _context: Context) -> None:  # noqa D417
    """
    Update time point (make sure the user can't selected an undifined time point).

    Args:
        _context (Context):
    """

    if self.end > self.max:
        self.end = self.max
    elif self.end < 0:
        self.end = 0


def update_plane_id(self, _context: Context) -> None:  # noqa D417
    """
    Update plane id (for 3D TELEMAC files, make sure the user can't selected an undifined plane id).

    Args:
        _context (Context): context
    """

    # -------------------------------- #
    # /!\ For testing purpose only /!\ #
    # -------------------------------- #
    try:
        if self.mode == 'TEST':
            return
    except Exception:
        pass

    if self.plane_id > self.max_plane_id:
        self.plane_id = self.max_plane_id
    elif self.plane_id < 0:
        self.plane_id = 0
