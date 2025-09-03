# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import time
import typing as ta

from omlish.logs.levels import LogLevel

from .bindings import CanTypedLoggerBinding
from .bindings import TypedLoggerBindings
from .bindings import as_typed_logger_bindings
from .contexts import TypedLoggerContext
from .types import TypedLoggerField
from .types import TypedLoggerFieldValue
from .values import StandardTypedLoggerValues


##


DEFAULT_TYPED_LOGGER_BINDINGS = TypedLoggerBindings(
    TypedLoggerField('time', StandardTypedLoggerValues.Time),
    TypedLoggerField('level', StandardTypedLoggerValues.LevelName),
    TypedLoggerField('msg', StandardTypedLoggerValues.Msg),
)


##


class TypedLogger(ta.Protocol):
    def log(
            self,
            level: LogLevel,
            msg: ta.Union[
                str,
                tuple,
                CanTypedLoggerBinding,
                None,
            ] = None,
            /,
            *items: CanTypedLoggerBinding,
            **kwargs: ta.Union[
                TypedLoggerFieldValue,
                ta.Any,
            ],
    ) -> None: ...


class TypedLoggerImpl:
    def __init__(
            self,
            bindings: TypedLoggerBindings,
    ) -> None:
        super().__init__()

        self._bindings = bindings

    def log(
            self,
            level: LogLevel,
            msg: ta.Union[
                str,
                tuple,
                CanTypedLoggerBinding,
                None,
            ] = None,
            /,
            *items: CanTypedLoggerBinding,
            **kwargs: ta.Union[
                TypedLoggerFieldValue,
                ta.Any,
            ],
    ) -> None:
        # LoggingCaller.
        bs = TypedLoggerBindings(
            self._bindings,
            StandardTypedLoggerValues.TimeNs(time.time_ns()),
            StandardTypedLoggerValues.Level(level),
            StandardTypedLoggerValues.Msg(ta.cast(str, msg)),
            *as_typed_logger_bindings(
                *items,
                *kwargs.items(),
                add_default_keys=True,
            ),
            override=True,
        )

        ctx = TypedLoggerContext(bs)

        for k, fv in ctx.bindings.key_map.items():
            print((k, ctx.unwrap_field_value(fv)))
        print()
