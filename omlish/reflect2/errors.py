class ReflectionError(Exception):
    pass


class ReflectionTypeError(ReflectionError):
    pass


class ReflectionValueError(ReflectionError):
    pass


class ReflectionRuntimeError(ReflectionError):
    pass


class ReflectionInternalError(ReflectionError):
    pass


class UnsupportedTypeOperationError(ReflectionTypeError):
    pass


class UnreflectableTypeError(ReflectionTypeError):
    pass


class ProtocolReflectionError(ReflectionTypeError):
    pass


class RecursiveTypeReflectionError(ReflectionTypeError):
    pass
