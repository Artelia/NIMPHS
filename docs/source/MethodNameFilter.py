from enchant.tokenize import Filter

class MethodNameFilter(Filter):
    """If a word looks like a method name, ignore it."""

    def _skip(self, word):
        if word[0].islower():
            # Method names usually have one or more uppercases characters after the first char.
            if sum(1 for char in word if char.isupper()) >= 1:
                return True
            else:
                False

        return False
