# <pep8 compliant>
from typing import Union


class TemporaryData():
    """Base class of temporary data for both modules."""

    def __init__(self) -> None:
        """Init method of the class."""

        self.module_name = ""
        self.nb_vars = 0
        self.nb_time_points = 0

    def update(self, file_path: str):
        pass

    def get_point_data(self, var: Union[str, int]):
        pass
