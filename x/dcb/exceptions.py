import types
import typing as ta


##


def _hands_off_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}@{hex(id(obj))[2:]}'


def _fn_repr(fn: ta.Callable) -> str:
    if (co := getattr(fn, '__code__', None)) is None or not isinstance(co, types.CodeType):
        return repr(fn)

    if not (co_filename := co.co_filename):
        return repr(fn)

    return f'{fn!r} ({co_filename}:{co.co_firstlineno})'


##


class ValidationError(Exception):
    def __init__(
            self,
            obj: ta.Any,
            fn: ta.Callable,
    ) -> None:
        self.obj = obj
        self.fn = fn

        super().__init__(self._build_message())

    def _build_message(self) -> str:
        return (
            f'{self.__class__.__name__} '
            f'on object {_hands_off_repr(self.obj)} '
            f'in validator {_fn_repr(self.fn)}'
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join([
            f"obj={_hands_off_repr(self.obj)}",
            f"fn={_fn_repr(self.fn)}",
        ])})'


class FieldValidationError(ValidationError):
    def __init__(
            self,
            obj: ta.Any,
            fn: ta.Callable,
            field: str,
            value: ta.Any,
    ) -> None:
        self.field = field
        self.value = value

        super().__init__(
            obj,
            fn,
        )

    def _build_message(self) -> str:
        return (
            f'{self.__class__.__name__} '
            f'on object {_hands_off_repr(self.obj)} '
            f'in validator {_fn_repr(self.fn)} '
            f'for field {self.field!r} '
            f'with value {self.value!r}'
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join([
            f"obj={_hands_off_repr(self.obj)}",
            f"fn={_fn_repr(self.fn)}",
            f"field={self.field!r}",
            f"value={self.value!r}",
        ])})'
