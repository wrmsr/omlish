# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - TypedDict?
"""
import abc
import logging
import typing as ta

from ...lite.abstract import Abstract
from ..contexts import LoggingContext
from ..infos import LoggingContextInfo
from ..infos import LoggingContextInfos
from ..infos import LoggingExcInfoTuple
from ..warnings import LoggingSetupWarning


T = ta.TypeVar('T')


##


# Ref:
#  - https://docs.python.org/3/library/logging.html#logrecord-attributes
#
# LogRecord:
#  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L276 (3.8)
#  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L286 (~3.14)  # noqa
#
# LogRecord.__init__ args:
#  - name: str
#  - level: int
#  - pathname: str - Confusingly referred to as `fn` before the LogRecord ctor. May be empty or "(unknown file)".
#  - lineno: int - May be 0.
#  - msg: str
#  - args: tuple | dict | 1-tuple[dict]
#  - exc_info: LoggingExcInfoTuple | None
#  - func: str | None = None -> funcName
#  - sinfo: str | None = None -> stack_info
#
KNOWN_STD_LOGGING_RECORD_ATTRS: ta.Dict[str, ta.Any] = dict(
    # Name of the logger used to log the call. Unmodified by ctor.
    name=str,

    # The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object
    # (see Using arbitrary objects as messages). Unmodified by ctor.
    msg=str,

    # The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when
    # there is only one argument, and it is a dictionary). Ctor will transform a 1-tuple containing a Mapping into just
    # the mapping, but is otherwise unmodified.
    args=ta.Union[tuple, dict],

    #

    # Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Set to
    # `getLevelName(level)`.
    levelname=str,

    # Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL). Unmodified by ctor.
    levelno=int,

    #

    # Full pathname of the source file where the logging call was issued (if available). Unmodified by ctor. May default
    # to "(unknown file)" by Logger.findCaller / Logger._log.
    pathname=str,

    # Filename portion of pathname. Set to `os.path.basename(pathname)` if successful, otherwise defaults to pathname.
    filename=str,

    # Module (name portion of filename). Set to `os.path.splitext(filename)[0]`, otherwise defaults to
    # "Unknown module".
    module=str,

    #

    # Exception tuple (à la sys.exc_info) or, if no exception has occurred, None. Unmodified by ctor.
    exc_info=ta.Optional[LoggingExcInfoTuple],

    # Used to cache the traceback text. Simply set to None by ctor, later set by Formatter.format.
    exc_text=ta.Optional[str],

    #

    # Stack frame information (where available) from the bottom of the stack in the current thread, up to and including
    # the stack frame of the logging call which resulted in the creation of this record. Set by ctor to `sinfo` arg,
    # unmodified. Mostly set, if requested, by `Logger.findCaller`, to `traceback.print_stack(f)`, but prepended with
    # the literal "Stack (most recent call last):\n", and stripped of exactly one trailing `\n` if present.
    stack_info=ta.Optional[str],

    # Source line number where the logging call was issued (if available). Unmodified by ctor. May default to 0 by
    # Logger.findCaller / Logger._log.
    lineno=int,

    # Name of function containing the logging call. Set by ctor to `func` arg, unmodified. May default to
    # "(unknown function)" by Logger.findCaller / Logger._log.
    funcName=str,

    #

    # Time when the LogRecord was created. Set to `time.time_ns() / 1e9` for >=3.13.0b1, otherwise simply `time.time()`.
    #
    # See:
    #  - https://github.com/python/cpython/commit/1316692e8c7c1e1f3b6639e51804f9db5ed892ea
    #  - https://github.com/python/cpython/commit/1500a23f33f5a6d052ff1ef6383d9839928b8ff1
    #
    created=float,

    # Millisecond portion of the time when the LogRecord was created.
    msecs=float,

    # Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
    relativeCreated=float,

    #

    # Thread ID if available, and `logging.logThreads` is truthy.
    thread=ta.Optional[int],

    # Thread name if available, and `logging.logThreads` is truthy.
    threadName=ta.Optional[str],

    #

    # Process name if available. Set to None if `logging.logMultiprocessing` is not truthy. Otherwise, set to
    # 'MainProcess', then `sys.modules.get('multiprocessing').current_process().name` if that works, otherwise remains
    # as 'MainProcess'.
    #
    # As noted by stdlib:
    #
    #   Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
    #   third-party code to run when multiprocessing calls import. See issue 8200 for an example
    #
    processName=ta.Optional[str],

    # Process ID if available - that is, if `hasattr(os, 'getpid')` - and `logging.logProcesses` is truthy, otherwise
    # None.
    process=ta.Optional[int],

    #

    # Absent <3.12, otherwise asyncio.Task name if available, and `logging.logAsyncioTasks` is truthy. Set to
    # `sys.modules.get('asyncio').current_task().get_name()`, otherwise None.
    taskName=ta.Optional[str],
)

KNOWN_STD_LOGGING_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(KNOWN_STD_LOGGING_RECORD_ATTRS)


# Formatter:
#  - https://github.com/python/cpython/blob/39b2f82717a69dde7212bc39b673b0f55c99e6a3/Lib/logging/__init__.py#L514 (3.8)
#  - https://github.com/python/cpython/blob/f070f54c5f4a42c7c61d1d5d3b8f3b7203b4a0fb/Lib/logging/__init__.py#L554 (~3.14)  # noqa
#
KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS: ta.Dict[str, ta.Any] = dict(
    # The logged message, computed as msg % args. Set to `record.getMessage()`.
    message=str,

    # Human-readable time when the LogRecord was created. By default this is of the form '2003-07-08 16:49:45,896' (the
    # numbers after the comma are millisecond portion of the time). Set to `self.formatTime(record, self.datefmt)` if
    # `self.usesTime()`, otherwise unset.
    asctime=str,

    # Used to cache the traceback text. If unset (falsey) on the record and `exc_info` is truthy, set to
    # `self.formatException(record.exc_info)` - otherwise unmodified.
    exc_text=ta.Optional[str],
)

KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTR_SET: ta.FrozenSet[str] = frozenset(KNOWN_STD_LOGGING_FORMATTER_RECORD_ATTRS)


##


class UnknownStdLoggingRecordAttrsWarning(LoggingSetupWarning):
    pass


def _check_std_logging_record_attrs() -> None:
    rec_dct = dict(logging.makeLogRecord({}).__dict__)

    if (unk_rec_fields := frozenset(rec_dct) - KNOWN_STD_LOGGING_RECORD_ATTR_SET):
        import warnings  # noqa

        warnings.warn(
            f'Unknown log record attrs detected: {sorted(unk_rec_fields)!r}',
            UnknownStdLoggingRecordAttrsWarning,
        )


_check_std_logging_record_attrs()


##


class LoggingContextInfoRecordAdapters:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class Adapter(Abstract, ta.Generic[T]):
        @abc.abstractmethod
        def info_to_record(self, info: T) -> ta.Mapping[str, ta.Any]:
            raise NotImplementedError

        @abc.abstractmethod
        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[T]:
            raise NotImplementedError

    #

    class Name(Adapter[LoggingContextInfos.Name]):
        def info_to_record(self, info: LoggingContextInfos.Name) -> ta.Mapping[str, ta.Any]:
            return dict(
                name=info.name,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Name:
            return LoggingContextInfos.Name(
                name=rec.name,
            )

    class Level(Adapter[LoggingContextInfos.Level]):
        def info_to_record(self, info: LoggingContextInfos.Level) -> ta.Mapping[str, ta.Any]:
            return dict(
                levelname=info.name,
                levelno=int(info.level),
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Level:
            return LoggingContextInfos.Level.build(rec.levelno)

    class Msg(Adapter[LoggingContextInfos.Msg]):
        def info_to_record(self, info: LoggingContextInfos.Msg) -> ta.Mapping[str, ta.Any]:
            return dict(
                msg=info.msg,
                args=info.args,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Msg:
            return LoggingContextInfos.Msg(
                msg=rec.msg,
                args=rec.args,
            )

    class Extra(Adapter[LoggingContextInfos.Extra]):
        def info_to_record(self, info: LoggingContextInfos.Extra) -> ta.Mapping[str, ta.Any]:
            # FIXME:
            # if extra is not None:
            #     for key in extra:
            #         if (key in ["message", "asctime"]) or (key in rv.__dict__):
            #             raise KeyError("Attempt to overwrite %r in LogRecord" % key)
            #         rv.__dict__[key] = extra[key]
            return dict()

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Extra]:
            return None

    class Time(Adapter[LoggingContextInfos.Time]):
        def info_to_record(self, info: LoggingContextInfos.Time) -> ta.Mapping[str, ta.Any]:
            return dict(
                created=info.secs,
                msecs=info.msecs,
                relativeCreated=info.relative_secs,
            )

        def record_to_info(self, rec: logging.LogRecord) -> LoggingContextInfos.Time:
            return LoggingContextInfos.Time.build(
                int(rec.created * 1e9),
            )

    class Exc(Adapter[LoggingContextInfos.Exc]):
        def info_to_record(self, info: ta.Optional[LoggingContextInfos.Exc]) -> ta.Mapping[str, ta.Any]:
            if info is not None:
                return dict(
                    exc_info=info.info_tuple,
                    exc_text=None,
                )
            else:
                return dict(
                    exc_info=None,
                    exc_text=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Exc]:
            # FIXME:
            # error: Argument 1 to "build" of "Exc" has incompatible type
            # "tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None"; expected  # noqa
            # "BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | bool | None"  [arg-type]  # noqa
            return LoggingContextInfos.Exc.build(rec.exc_info)  # type: ignore[arg-type]

    class Caller(Adapter[LoggingContextInfos.Caller]):
        _UNKNOWN_PATH_NAME: ta.ClassVar[str] = '(unknown file)'
        _UNKNOWN_FUNC_NAME: ta.ClassVar[str] = '(unknown function)'

        _STACK_INFO_PREFIX: ta.ClassVar[str] = 'Stack (most recent call last):\n'

        def info_to_record(self, caller: ta.Optional[LoggingContextInfos.Caller]) -> ta.Mapping[str, ta.Any]:
            if caller is not None:
                if (sinfo := caller.stack_info) is not None:
                    stack_info: ta.Optional[str] = '\n'.join([
                        self._STACK_INFO_PREFIX,
                        sinfo[1:] if sinfo.endswith('\n') else sinfo,
                    ])
                else:
                    stack_info = None

                return dict(
                    pathname=caller.file_path,

                    lineno=caller.line_no,
                    funcName=caller.func_name,

                    stack_info=stack_info,
                )

            else:
                return dict(
                    pathname=self._UNKNOWN_PATH_NAME,

                    lineno=0,
                    funcName=self._UNKNOWN_FUNC_NAME,

                    stack_info=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Caller]:
            # FIXME: piecemeal?
            # FIXME: strip _STACK_INFO_PREFIX
            raise NotImplementedError

    class SourceFile(Adapter[LoggingContextInfos.SourceFile]):
        _UNKNOWN_MODULE: ta.ClassVar[str] = 'Unknown module'

        def info_to_record(
                self,
                info: ta.Optional[LoggingContextInfos.SourceFile],
                *,
                caller_file_path: ta.Optional[str] = None,
        ) -> ta.Mapping[str, ta.Any]:
            if info is not None:
                return dict(
                    filename=info.file_name,
                    module=info.module,
                )
            else:
                return dict(
                    filename=caller_file_path,
                    module=self._UNKNOWN_MODULE,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.SourceFile]:
            if not (
                    rec.module is None or
                    rec.module == self._UNKNOWN_MODULE
            ):
                return LoggingContextInfos.SourceFile(
                    file_name=rec.filename,
                    module=rec.module,  # FIXME: piecemeal?
                )
            else:
                return None

    class Thread(Adapter[ta.Optional[LoggingContextInfos.Thread]]):
        def info_to_record(self, info: ta.Optional[LoggingContextInfos.Thread]) -> ta.Mapping[str, ta.Any]:
            if (
                    info is not None and
                    logging.logThreads
            ):
                return dict(
                    thread=info.ident,
                    threadName=info.name,
                )
            else:
                return dict(
                    thread=None,
                    threadName=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Thread]:
            if (
                    (ident := rec.thread) is not None and
                    (name := rec.threadName) is not None
            ):
                return LoggingContextInfos.Thread(
                    ident=ident,
                    native_id=None,
                    name=name,
                )
            else:
                return None

    class Process(Adapter[ta.Optional[LoggingContextInfos.Process]]):
        def info_to_record(self, info: ta.Optional[LoggingContextInfos.Process]) -> ta.Mapping[str, ta.Any]:
            if (
                    info is not None and
                    logging.logProcesses
            ):
                return dict(
                    process=info.pid,
                )
            else:
                return dict(
                    process=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Process]:
            if (
                    (pid := rec.process) is not None
            ):
                return LoggingContextInfos.Process(
                    pid=pid,
                )
            else:
                return None

    class Multiprocessing(Adapter[ta.Optional[LoggingContextInfos.Multiprocessing]]):
        def info_to_record(self, info: ta.Optional[LoggingContextInfos.Multiprocessing]) -> ta.Mapping[str, ta.Any]:
            if (
                    info is not None and
                    logging.logMultiprocessing
            ):
                return dict(
                    processName=info.process_name,
                )
            else:
                return dict(
                    processName=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.Multiprocessing]:
            if (
                    (process_name := rec.processName) is not None
            ):
                return LoggingContextInfos.Multiprocessing(
                    process_name=process_name,
                )
            else:
                return None

    class AsyncioTask(Adapter[ta.Optional[LoggingContextInfos.AsyncioTask]]):
        def info_to_record(self, info: ta.Optional[LoggingContextInfos.AsyncioTask]) -> ta.Mapping[str, ta.Any]:
            if not hasattr(logging, 'logAsyncioTasks'):  # Absent <3.12
                return dict()
            elif (
                    info is not None and
                    getattr(logging, 'logAsyncioTasks', None)  # Absent <3.12
            ):
                return dict(
                    taskName=info.name,
                )
            else:
                return dict(
                    taskName=None,
                )

        def record_to_info(self, rec: logging.LogRecord) -> ta.Optional[LoggingContextInfos.AsyncioTask]:
            if (
                    (name := getattr(rec, 'taskName', None)) is not None
            ):
                return LoggingContextInfos.AsyncioTask(
                    name=name,
                )
            else:
                return None


_LOGGING_CONTEXT_INFO_RECORD_ADAPTERS: ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfoRecordAdapters.Adapter] = {  # noqa
    LoggingContextInfos.Name: LoggingContextInfoRecordAdapters.Name(),
    LoggingContextInfos.Level: LoggingContextInfoRecordAdapters.Level(),
    LoggingContextInfos.Msg: LoggingContextInfoRecordAdapters.Msg(),
    LoggingContextInfos.Extra: LoggingContextInfoRecordAdapters.Extra(),
    LoggingContextInfos.Time: LoggingContextInfoRecordAdapters.Time(),
    LoggingContextInfos.Exc: LoggingContextInfoRecordAdapters.Exc(),
    LoggingContextInfos.Caller: LoggingContextInfoRecordAdapters.Caller(),
    LoggingContextInfos.SourceFile: LoggingContextInfoRecordAdapters.SourceFile(),
    LoggingContextInfos.Thread: LoggingContextInfoRecordAdapters.Thread(),
    LoggingContextInfos.Process: LoggingContextInfoRecordAdapters.Process(),
    LoggingContextInfos.Multiprocessing: LoggingContextInfoRecordAdapters.Multiprocessing(),
    LoggingContextInfos.AsyncioTask: LoggingContextInfoRecordAdapters.AsyncioTask(),
}


class LoggingContextLogRecord(logging.LogRecord):
    def __init__(self, *, _logging_context: LoggingContext) -> None:  # noqa
        for it, ad in _LOGGING_CONTEXT_INFO_RECORD_ADAPTERS.items():
            self.__dict__.update(ad.info_to_record(_logging_context[it]))
