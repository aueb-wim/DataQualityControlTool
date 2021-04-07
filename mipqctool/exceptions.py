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

class TableReportError(QCToolException):
    pass

class DockerExecError(QCToolException):
    pass

class MappingValidationError(QCToolException):
    pass

class MappingError(QCToolException):
    pass

class FunctionNameError(QCToolException):
    pass

class ArgsFunctionError(QCToolException):
    pass

class ExpressionError(QCToolException):
    pass

class ColumnNameError(QCToolException):
    pass