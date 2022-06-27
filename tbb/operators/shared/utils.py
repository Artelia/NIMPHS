# <pep8 compliant>
from bpy.types import Context

import logging
log = logging.getLogger(__name__)


def update_start(self, _context: Context) -> None:
    """
    Update time point (make sure the user can't selected an undifined time point).

    Args:
        context (Context):
    """

    if self.start > self.max - 2:
        self.start = self.max - 2
    elif self.start < 0:
        self.start = 0


def update_end(self, _context: Context) -> None:
    """
    Update time point (make sure the user can't selected an undifined time point).

    Args:
        context (Context):
    """

    if self.end > self.max - 1:
        self.end = self.max - 1
    elif self.end < 0:
        self.end = 0
