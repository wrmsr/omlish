import logging  # noqa
import types  # noqa
import typing as ta  # noqa

from omlish import logs


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


class Formatter:
    default_time_format: ta.ClassVar[str]
    default_msec_format: ta.ClassVar[str]

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str: ...

    def formatException(self, ei: ExceptionInfo) -> str: ...

    def usesTime(self) -> bool: ...

    def formatMessage(self, record: LogRecord) -> str: ...

    def formatStack(self, stack_info: str) -> str: ...

    def format(self, record: LogRecord) -> str: ...


class BufferingFormatter:

    def formatHeader(self, records: ta.Sequence[LogRecord]) -> str: ...

    def formatFooter(self, records: ta.Sequence[LogRecord]) -> str: ...

    def format(self, records: ta.Sequence[LogRecord]) -> str: ...


##


class Filter:
    def filter(self, record: LogRecord) -> bool: ...


class Filterer:
    def addFilter(self, filter: Filter) -> None: ...

    def removeFilter(self, filter: Filter) -> None: ...

    def filter(self, record: LogRecord) -> bool: ...


##


class Handler:
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


class Manager:
    root: 'Logger'

    disable: Level

    def getLogger(self, name: str) -> ta.Optional['Logger']: ...

    def setLoggerClass(self, klass: type['Logger']) -> None: ...

    def setLogRecordFactory(self, factory: ta.Callable[..., LogRecord]) -> None: ...  # UNREFERENCED?


##


class Logger(Filterer):
    name: str
    level: Level
    parent: ta.Optional['Logger']
    propagate: bool
    handlers: list[Handler]
    disabled: bool

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


##


def _main():
    logs.configure_standard_logging(logging.INFO)
    try:
        raise ValueError('barf')
    except Exception:
        logging.info('hi', stack_info=True, exc_info=True)


if __name__ == '__main__':
    _main()
