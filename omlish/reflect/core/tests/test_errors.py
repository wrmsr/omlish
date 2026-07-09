from ...errors import ReflectionError
from ...errors import ReflectionRuntimeError
from ...errors import ReflectionTypeError
from ...errors import ReflectionValueError
from ...errors import UnreflectableTypeError
from ...errors import UnsupportedTypeOperationError


def test_named_errors_share_reflection_base() -> None:
    assert issubclass(UnsupportedTypeOperationError, ReflectionError)
    assert issubclass(UnreflectableTypeError, ReflectionError)


def test_reflection_errors_do_not_subclass_builtin_error_families() -> None:
    for error_cls in (ReflectionTypeError, ReflectionValueError, ReflectionRuntimeError):
        assert issubclass(error_cls, ReflectionError)
        assert not issubclass(error_cls, TypeError)
        assert not issubclass(error_cls, ValueError)
        assert not issubclass(error_cls, RuntimeError)
