

class InvalidFileError(Exception):
    def __init__(self, value):
        self._parameter = value

    def __str__(self):
        return  repr(self._parameter)