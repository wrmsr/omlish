# ruff: noqa: A002
# ruff: noqa: N802
# ruff: noqa: N815

import types
import typing as ta


##


Level: ta.TypeAlias = int


ExceptionInfo: ta.TypeAlias = tuple[type[BaseException], BaseException, types.TracebackType]


class LogRecord:
    name: str
    msg: str
    args: tuple
    levelname: str
    levelno: Level
    pathname: str
    filename: str
    module: str
    exc_info: ExceptionInfo | None
    exc_text: str | None
    stack_info: str | None
    lineno: int
    funcName: str
    created: float
    msecs: float
    relativeCreated: float
    thread: int
    threadName: str
    processName: str
    process: int


##


class Formatter(ta.Protocol):
    default_time_format: ta.ClassVar[str]
    default_msec_format: ta.ClassVar[str]

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str: ...

    def formatException(self, ei: ExceptionInfo) -> str: ...

    def usesTime(self) -> bool: ...

    def formatMessage(self, record: LogRecord) -> str: ...

    def formatStack(self, stack_info: str) -> str: ...

    def format(self, record: LogRecord) -> str: ...


class BufferingFormatter(ta.Protocol):
    def formatHeader(self, records: ta.Sequence[LogRecord]) -> str: ...

    def formatFooter(self, records: ta.Sequence[LogRecord]) -> str: ...

    def format(self, records: ta.Sequence[LogRecord]) -> str: ...


##


class Filter(ta.Protocol):
    def filter(self, record: LogRecord) -> bool: ...


class Filterer(ta.Protocol):
    def addFilter(self, filter: Filter) -> None: ...

    def removeFilter(self, filter: Filter) -> None: ...

    def filter(self, record: LogRecord) -> bool: ...


##


class Handler(ta.Protocol):
    level: Level

    def get_name(self) -> str: ...

    def set_name(self, name: str) -> None: ...

    name: str

    def createLock(self) -> None: ...

    def acquire(self) -> None: ...

    def release(self) -> None: ...

    def setLevel(self, level: Level) -> None: ...

    def format(self, record: LogRecord) -> str: ...

    def emit(self, record: LogRecord) -> None: ...

    def handle(self, record: LogRecord) -> bool: ...

    def setFormatter(self, fmt: Formatter) -> None: ...

    def flush(self) -> None: ...

    def close(self) -> None: ...

    def handleError(self, record: LogRecord) -> None: ...


class Stream(ta.Protocol):
    def write(self, s: str) -> None: ...

    def flush(self) -> None: ...  # OPTIONAL METHOD

    def close(self) -> None: ...  # OPTIONAL METHOD


class StreamHandler(Handler):
    terminator: ta.ClassVar[str]

    stream: Stream

    def flush(self) -> None: ...

    def emit(self, record: LogRecord) -> None: ...

    def setStream(self, stream: Stream) -> None: ...


##


class Manager(ta.Protocol):
    root: 'Logger'

    disable: Level

    def getLogger(self, name: str) -> 'Logger': ...

    def setLoggerClass(self, klass: type['Logger']) -> None: ...

    def setLogRecordFactory(self, factory: ta.Callable[..., LogRecord]) -> None: ...  # UNREFERENCED?


##


Caller: ta.TypeAlias = tuple[
    str,  # filename
    int,  # lineno
    str,  # name
    str,  # formatted
]


class Logger(Filterer, ta.Protocol):
    name: str
    level: Level
    parent: ta.Optional['Logger']
    propagate: bool
    handlers: list[Handler]
    disabled: bool

    manager: Manager

    def setLevel(self, level: Level) -> None: ...

    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warn(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def exception(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def fatal(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def log(self, level: Level, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def findCaller(self, stack_info: bool = False, stacklevel: int = 1) -> Caller: ...

    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func: str | None = None,
        extra: ta.Mapping[str, ta.Any] | None = None,
        sinfo: str | None = None,
    ) -> LogRecord: ...

    def handle(self, record: LogRecord) -> None: ...

    def addHandler(self, hdlr: Handler) -> None: ...

    def removeHandler(self, hdlr: Handler) -> None: ...

    def hasHandlers(self) -> bool: ...

    def callHandlers(self, record: LogRecord) -> None: ...

    def getEffectiveLevel(self) -> Level: ...

    def isEnabledFor(self, level: Level) -> bool: ...

    def getChild(self, suffix: str) -> 'Logger': ...


##


class LoggerAdapter(ta.Protocol):
    logger: Logger
    extra: ta.Mapping[str, ta.Any]

    def process(self, msg: str, kwargs: dict[str, ta.Any]) -> tuple[str, dict[str, ta.Any]]: ...

    def debug(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def info(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warning(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warn(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def error(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def exception(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def critical(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def fatal(self, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def log(self, level: Level, msg: str, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def isEnabledFor(self, level: Level) -> bool: ...

    def setLevel(self, level: Level) -> None: ...

    def getEffectiveLevel(self) -> Level: ...

    def hasHandlers(self) -> bool: ...

    manager: Manager

    name: str
