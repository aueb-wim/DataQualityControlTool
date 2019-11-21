# exceptions.py


class QCToolException(Exception):

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


class DataTypeError(QCToolException):
    pass

class ConstraintViolationError(QCToolException):
    pass
