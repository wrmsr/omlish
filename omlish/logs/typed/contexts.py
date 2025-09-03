# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .types import ABSENT_TYPED_LOGGER_VALUE
from .types import AbsentTypedLoggerValue
from .types import ResolvedTypedLoggerFieldValue
from .types import TypedLoggerFieldValue
from .types import TypedLoggerValue
from .types import TypedLoggerValueOrAbsent
from .types import UnwrappedTypedLoggerFieldValue
from .types import unwrap_typed_logger_field_value


if ta.TYPE_CHECKING:
    from .bindings import TypedLoggerBindings


TypedLoggerValueT = ta.TypeVar('TypedLoggerValueT', bound='TypedLoggerValue')


##


class RecursiveTypedLoggerValueError(Exception):
    def __init__(self, cls: ta.Type[TypedLoggerValue], rec: ta.Sequence[ta.Type[TypedLoggerValue]]) -> None:
        super().__init__()

        self.cls = cls
        self.rec = rec

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'cls={self.cls!r}, '
            f'rec={self.rec!r}'
            f')'
        )


class UnboundTypedLoggerValueError(Exception):
    def __init__(self, cls: ta.Type[TypedLoggerValue]) -> None:
        super().__init__()

        self.cls = cls

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(cls={self.cls!r})'


#


@ta.final
class TypedLoggerContext:
    def __init__(
            self,
            bindings: 'TypedLoggerBindings',
            *,
            no_auto_default_values: bool = False,
            default_absent: bool = False,
    ) -> None:
        super().__init__()

        self._bindings = bindings
        self._no_auto_default_values = no_auto_default_values
        self._default_absent = default_absent

        self._values: ta.Dict[ta.Type[TypedLoggerValue], TypedLoggerValueOrAbsent] = dict(bindings.const_value_map)  # noqa
        self._rec: ta.Dict[ta.Type[TypedLoggerValue], None] = {}

    @property
    def bindings(self) -> 'TypedLoggerBindings':
        return self._bindings

    @property
    def no_auto_default_values(self) -> bool:
        return self._no_auto_default_values

    @property
    def default_absent(self) -> bool:
        return self._default_absent

    #

    def __getitem__(self, cls: ta.Type[TypedLoggerValueT]) -> ta.Union[TypedLoggerValueT, AbsentTypedLoggerValue]:
        try:
            return self._values[cls]  # type: ignore[return-value]
        except KeyError:
            pass

        if not issubclass(cls, TypedLoggerValue):
            raise TypeError(cls)

        if cls in self._rec:
            raise RecursiveTypedLoggerValueError(cls, list(self._rec))

        self._rec[cls] = None
        try:
            v: ta.Union[TypedLoggerValueOrAbsent]

            if (bv := self._bindings.lookup_value(cls)) is not None:
                if bv is ABSENT_TYPED_LOGGER_VALUE:  # noqa
                    v = ABSENT_TYPED_LOGGER_VALUE

                else:
                    v = bv._typed_logger_provide_value(self)  # noqa

            else:
                if not self._no_auto_default_values and (dt := cls._typed_logger_maybe_provide_default_value(self)):
                    [v] = dt

                elif self._default_absent:
                    v = ABSENT_TYPED_LOGGER_VALUE

                else:
                    raise UnboundTypedLoggerValueError(cls) from None

            self._values[cls] = v
            return v  # type: ignore[return-value]

        finally:
            self._rec.pop(cls)

    #

    def resolve_field_value(self, fv: TypedLoggerFieldValue) -> ResolvedTypedLoggerFieldValue:
        if fv is ABSENT_TYPED_LOGGER_VALUE:
            return fv  # type: ignore[return-value]

        elif isinstance(fv, type):
            return self[fv]._typed_logger_resolve_field_value(self)  # type: ignore[type-var]  # noqa

        else:
            return fv._typed_logger_resolve_field_value(self)  # noqa

    def unwrap_field_value(self, fv: TypedLoggerFieldValue) -> UnwrappedTypedLoggerFieldValue:
        return unwrap_typed_logger_field_value(self.resolve_field_value(fv))
