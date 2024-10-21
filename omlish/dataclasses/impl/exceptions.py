import types
import typing as ta


class ValidationError(Exception):
    pass


def _hands_off_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}@{hex(id(obj))[2:]}'


def _fn_repr(fn: ta.Callable) -> str:
    if (co := getattr(fn, '__code__', None)) is None or not isinstance(co, types.CodeType):
        return repr(fn)

    if not (co_filename := co.co_filename):
        return repr(fn)

    return f'{fn!r} ({co_filename}:{co.co_firstlineno})'


class FieldValidationError(ValidationError):
    def __init__(
            self,
            obj: ta.Any,
            field: str,
            fn: ta.Callable,
            value: ta.Any,
    ) -> None:
        super().__init__(
            f'{self.__class__.__name__} '
            f'for field {field!r} '
            f'on object {_hands_off_repr(obj)} '
            f'in validator {_fn_repr(fn)} '
            f'with value {value!r}',
        )

        self.obj = obj
        self.field = field
        self.fn = fn
        self.value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join([
            f"obj={_hands_off_repr(self.obj)}",
            f"field={self.field!r}",
            f"fn={_fn_repr(self.fn)}",
            f"value={self.value!r}",
        ])})'
