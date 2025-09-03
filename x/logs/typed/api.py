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
from .types import TypedLoggerValue
from .types import ABSENT_TYPED_LOGGER_VALUE
from .values import StandardTypedLoggerValues
from .types import ConstTypedLoggerValueProvider


##


DEFAULT_TYPED_LOGGER_BINDINGS = TypedLoggerBindings(
    TypedLoggerField('time', StandardTypedLoggerValues.Time),
    TypedLoggerField('level', StandardTypedLoggerValues.LevelName),
    TypedLoggerField('msg', StandardTypedLoggerValues.Msg),
)

_ABSENT_TYPED_LOGGER_MSG_PROVIDER = ConstTypedLoggerValueProvider(StandardTypedLoggerValues.Msg, ABSENT_TYPED_LOGGER_VALUE)  # noqa


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
        # TODO: log(INFO, lambda: (...))

        msg_items: ta.Sequence[CanTypedLoggerBinding]
        if msg is None:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER,)
        elif isinstance(msg, str):
            msg_items = (StandardTypedLoggerValues.Msg(msg),)
        elif isinstance(msg, tuple):
            msg_items = (StandardTypedLoggerValues.Msg(msg[0] % msg[1:]),)
        else:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER, msg)

        # LoggingCaller.

        bs = TypedLoggerBindings(
            self._bindings,
            StandardTypedLoggerValues.TimeNs(time.time_ns()),
            StandardTypedLoggerValues.Level(level),
            *as_typed_logger_bindings(
                *msg_items,
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
