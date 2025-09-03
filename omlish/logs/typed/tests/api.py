# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import logging
import sys
import time
import typing as ta

from ...callers import LoggingCaller
from ...levels import LogLevel
from ..bindings import CanTypedLoggerBinding
from ..bindings import FullTypedLoggerBindings
from ..bindings import TypedLoggerBindings
from ..bindings import as_typed_logger_bindings
from ..contexts import TypedLoggerContext
from ..types import ABSENT_TYPED_LOGGER_VALUE
from ..types import ConstTypedLoggerValueProvider
from ..types import TypedLoggerField
from ..types import TypedLoggerFieldValue
from ..values import StandardTypedLoggerValues


##


DEFAULT_TYPED_LOGGER_BINDINGS = FullTypedLoggerBindings(
    TypedLoggerField('time', StandardTypedLoggerValues.Time),
    TypedLoggerField('level', StandardTypedLoggerValues.LevelName),
    TypedLoggerField('msg', StandardTypedLoggerValues.Msg),
)

_ABSENT_TYPED_LOGGER_MSG_PROVIDER = ConstTypedLoggerValueProvider(StandardTypedLoggerValues.Msg, ABSENT_TYPED_LOGGER_VALUE)  # noqa


##


class TypedLogger:
    def __init__(
            self,
            bindings: TypedLoggerBindings,
            *,
            level: LogLevel = logging.INFO,
    ) -> None:
        super().__init__()

        self._bindings = bindings
        self._level = level

    #

    def info(
            self,
            msg: ta.Union[
                str,
                tuple,
                CanTypedLoggerBinding,
                ta.Callable[
                    [],
                    ta.Sequence[ta.Union[
                        str,
                        tuple,
                        CanTypedLoggerBinding,
                        None,
                    ]],
                ],
                None,
            ] = None,
            /,
            *items: CanTypedLoggerBinding,

            _logging_stack_offset: int = 0,

            **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None:
        return self.log(
            logging.INFO,
            msg,
            *items,

            _logging_stack_offset=_logging_stack_offset + 1,

            **kwargs,  # type: ignore[arg-type]
        )

    #

    def log(
            self,
            level: LogLevel,
            msg: ta.Union[
                str,
                tuple,
                CanTypedLoggerBinding,
                ta.Callable[
                    [],
                    ta.Sequence[ta.Union[
                        str,
                        tuple,
                        CanTypedLoggerBinding,
                        None,
                    ]],
                ],
                None,
            ] = None,
            /,
            *items: CanTypedLoggerBinding,

            _logging_exc_info: ta.Union[BaseException, tuple, bool] = False,

            _logging_stack_offset: int = 0,
            _logging_stack_info: bool = False,

            **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None:
        if _logging_exc_info is True:
            _logging_exc_info = sys.exc_info()

        if self._level < level:
            return

        if (
                callable(msg) and
                not isinstance(msg, type)  # it may be a type[TypedLoggerValue]
        ):
            t = msg()  # noqa

            if isinstance(t, str):
                msg = t

            elif not t:
                msg = None

            else:
                raise NotImplementedError

        self._do_log(
            level,
            msg,
            *items,

            _logging_exc_info=_logging_exc_info,

            _logging_stack_offset=_logging_stack_offset + 1,
            _logging_stack_info=_logging_stack_info,

            **kwargs,
        )

    def _do_log(
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

            _logging_exc_info: ta.Union[BaseException, tuple, bool] = False,

            _logging_stack_offset: int = 0,
            _logging_stack_info: bool = False,

            **kwargs: ta.Union[TypedLoggerFieldValue, ta.Any],
    ) -> None:
        # TODO: log(INFO, lambda: (...))

        if _logging_exc_info is True:
            _logging_exc_info = sys.exc_info()

        caller = LoggingCaller.find(  # noqa
            _logging_stack_offset,
            stack_info=_logging_stack_info,
        )

        msg_items: ta.Sequence[CanTypedLoggerBinding]
        if msg is None:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER,)
        elif isinstance(msg, str):
            msg_items = (StandardTypedLoggerValues.Msg(msg),)
        elif isinstance(msg, tuple):
            msg_items = (StandardTypedLoggerValues.Msg(msg[0] % msg[1:]),)
        else:
            msg_items = (_ABSENT_TYPED_LOGGER_MSG_PROVIDER, msg)

        bs = FullTypedLoggerBindings(
            self._bindings,
            StandardTypedLoggerValues.TimeNs(time.time_ns()),
            StandardTypedLoggerValues.Level(level),
            *as_typed_logger_bindings(
                *msg_items,
                *items,
                *kwargs.items(),
                add_default_keys=True,
                value_wrapper=self._bindings.value_wrapper_fn,
            ),
            override=True,
        )

        ctx = TypedLoggerContext(bs)

        for k, fv in ctx.bindings.key_map.items():
            print((k, ctx.unwrap_field_value(fv)))
        print()
