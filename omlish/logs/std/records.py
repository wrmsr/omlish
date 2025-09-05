# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import collections.abc
import logging
import sys
import typing as ta

from ...lite.check import check
from ..contexts import LoggingContext
from ..contexts import LoggingExcInfoTuple
from ..warnings import LoggingSetupWarning


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


class LoggingContextLogRecord(logging.LogRecord):
    _SHOULD_ADD_TASK_NAME: ta.ClassVar[bool] = sys.version_info >= (3, 12)

    _UNKNOWN_PATH_NAME: ta.ClassVar[str] = '(unknown file)'
    _UNKNOWN_FUNC_NAME: ta.ClassVar[str] = '(unknown function)'
    _UNKNOWN_MODULE: ta.ClassVar[str] = 'Unknown module'

    _STACK_INFO_PREFIX: ta.ClassVar[str] = 'Stack (most recent call last):\n'

    def __init__(  # noqa
            self,
            # name,
            # level,
            # pathname,
            # lineno,
            # msg,
            # args,
            # exc_info,
            # func=None,
            # sinfo=None,
            # **kwargs,
            *,
            name: str,
            msg: str,
            args: ta.Union[tuple, dict],

            _logging_context: LoggingContext,
    ) -> None:
        ctx = _logging_context

        self.name: str = name

        self.msg: str = msg

        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L307
        if args and len(args) == 1 and isinstance(args[0], collections.abc.Mapping) and args[0]:
            args = args[0]  # type: ignore[assignment]
        self.args: ta.Union[tuple, dict] = args

        self.levelname: str = logging.getLevelName(ctx.level)
        self.levelno: int = ctx.level

        if (caller := ctx.caller()) is not None:
            self.pathname: str = caller.file_path
        else:
            self.pathname = self._UNKNOWN_PATH_NAME

        if (src_file := ctx.source_file()) is not None:
            self.filename: str = src_file.file_name
            self.module: str = src_file.module
        else:
            self.filename = self.pathname
            self.module = self._UNKNOWN_MODULE

        self.exc_info: ta.Optional[LoggingExcInfoTuple] = ctx.exc_info_tuple
        self.exc_text: ta.Optional[str] = None

        # If ctx.build_caller() was never called, we simply don't have a stack trace.
        if caller is not None:
            if (sinfo := caller.stack_info) is not None:
                self.stack_info: ta.Optional[str] = '\n'.join([
                    self._STACK_INFO_PREFIX,
                    sinfo[1:] if sinfo.endswith('\n') else sinfo,
                ])
            else:
                self.stack_info = None

            self.lineno: int = caller.line_no
            self.funcName: str = caller.name

        else:
            self.stack_info = None

            self.lineno = 0
            self.funcName = self._UNKNOWN_FUNC_NAME

        times = ctx.times
        self.created: float = times.created
        self.msecs: float = times.msecs
        self.relativeCreated: float = times.relative_created

        if logging.logThreads:
            thread = check.not_none(ctx.thread())
            self.thread: ta.Optional[int] = thread.ident
            self.threadName: ta.Optional[str] = thread.name
        else:
            self.thread = None
            self.threadName = None

        if logging.logProcesses:
            process = check.not_none(ctx.process())
            self.process: ta.Optional[int] = process.pid
        else:
            self.process = None

        if logging.logMultiprocessing:
            if (mp := ctx.multiprocessing()) is not None:
                self.processName: ta.Optional[str] = mp.process_name
            else:
                self.processName = None
        else:
            self.processName = None

        # Absent <3.12
        if getattr(logging, 'logAsyncioTasks', None):
            if (at := ctx.asyncio_task()) is not None:
                self.taskName: ta.Optional[str] = at.name
            else:
                self.taskName = None
        else:
            self.taskName = None
