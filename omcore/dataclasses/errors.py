import types
import typing as ta


##


def _hands_off_repr(obj: ta.Any) -> str:
    return f'{obj.__class__.__qualname__}@{id(obj):x}'


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
            *,
            obj: ta.Any,
    ) -> None:
        self.obj = obj

        super().__init__(
            f'{self.__class__.__name__} '
            f'{", ".join(f"{k} {v}" for k, v in self._message_parts.items())}',
        )

    @property
    def _message_parts(self) -> ta.Mapping[str, str]:
        return {
            'obj': _hands_off_repr(self.obj),
        }

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join([
            f"{k}={v}" for k, v in self._message_parts.items()
        ])})'


class FnValidationError(ValidationError):
    def __init__(
            self,
            *,
            fn: ta.Callable,
            **kwargs: ta.Any,
    ) -> None:
        self.fn = fn

        super().__init__(**kwargs)

    @property
    def _message_parts(self) -> ta.Mapping[str, str]:
        return {
            **super()._message_parts,
            'fn': _fn_repr(self.fn),
        }


class FieldValidationError(ValidationError):
    def __init__(
            self,
            *,
            field: str,
            value: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self.field = field
        self.value = value

        super().__init__(**kwargs)

    @property
    def _message_parts(self) -> ta.Mapping[str, str]:
        return {
            **super()._message_parts,
            'field': repr(self.field),
            'value': repr(self.value),
        }


class FieldFnValidationError(FieldValidationError, FnValidationError):
    pass


class TypeValidationError(ValidationError, TypeError):
    def __init__(
            self,
            *,
            type: ta.Any,  # noqa
            **kwargs: ta.Any,
    ) -> None:
        self.type = type

        super().__init__(**kwargs)

    @property
    def _message_parts(self) -> ta.Mapping[str, str]:
        return {
            **super()._message_parts,
            'type': repr(self.type),
        }


class FieldTypeValidationError(FieldValidationError, TypeValidationError):
    pass
