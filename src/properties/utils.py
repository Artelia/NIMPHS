# <pep8 compliant>

def set_sequence_anim_length(self, value: int) -> None:
    """
    Function triggered when the user sets a new animation length. This let us to make sure the new value
    is not higher than the available time steps.

    Args:
        value (int): new value
    """

    if value > self.max_length:
        self["anim_length"] = self.max_length
    elif value < 0:
        self["anim_length"] = 0
    else:
        self["anim_length"] = value


def get_sequence_anim_length(self) -> int:
    """
    Return the animation length value.

    Returns:
        int: value
    """

    return self.get("anim_length", 0)
