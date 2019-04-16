# exceptions.py


class DicomSchemaException(Exception):

    # Public

    def __init__(self, message, errors=[]):
        self.__errors = errors
        super().__init__(message)

    @property
    def multiple(self):
        return bool(self.__errors)

    @property
    def errors(self):
        return self.__errors


class ValidationError(DicomSchemaException):
    pass
