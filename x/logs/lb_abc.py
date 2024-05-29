import datetime
import sys
import types
import typing as ta

import logbook


Level: ta.TypeAlias = int


ExceptionInfo: ta.TypeAlias = tuple[type[BaseException], BaseException, types.TracebackType]


class LogRecord:
    keep_open: bool
    time: datetime.datetime
    heavy_initialized: bool
    late: bool
    information_pulled: bool

    channel: str
    msg: str
    args: tuple
    kwargs: dict[str, ta.Any]
    level: Level
    exc_info: ExceptionInfo | None
    extra: ta.DefaultDict[str, ta.Any]
    frame: types.FrameType | None
    frame_correction: int
    process: int

    def heavy_init(self) -> None: ...

    def pull_information(self) -> None: ...

    def close(self) -> None: ...

    def to_dict(self, json_safe: bool = False) -> dict[str, ta.Any]: ...

    @classmethod
    def from_dict(cls, d: ta.Mapping[str, ta.Any]) -> 'LogRecord': ...

    def update_from_dict(self, d: ta.Mapping[str, ta.Any]) -> 'LogRecord': ...

    @property
    def message(self) -> str: ...

    @property
    def calling_frame(self) -> types.FrameType: ...

    @property
    def func_name(self) -> str: ...

    @property
    def module(self) -> str: ...

    @property
    def filename(self) -> str: ...

    @property
    def lineno(self) -> int: ...

    @property
    def greenlet(self) -> int: ...

    @property
    def thread(self) -> int: ...

    @property
    def thread_name(self) -> str: ...

    @property
    def process_name(self) -> str: ...

    @property
    def formatted_exception(self) -> str: ...

    @property
    def exception_name(self) -> str: ...

    @property
    def exception_shortname(self) -> str: ...

    @property
    def exception_message(self) -> str: ...

    @property
    def dispatcher(self) -> 'RecordDispatcher': ...


class LoggerMixin:
    @property
    def level_name(self) -> str: ...

    def trace(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def debug(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def info(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warn(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def warning(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def notice(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def error(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def exception(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...
    def critical(self, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def log(self, level: Level, *args: ta.Any, **kwargs: ta.Any) -> None: ...

    def catch_exceptions(self, *args: ta.Any, **kwargs: ta.Any) -> ta.ContextManager[None]: ...

    def enable(self) -> None: ...
    def disable(self) -> None: ...


class RecordDispatcher:
    suppress_dispatcher: bool

    @property
    def disabled(self) -> bool: ...

    @property
    def level(self) -> Level: ...

    def handle(self, record: LogRecord) -> None: ...

    def make_record_and_handle(
            self,
            level: Level,
            msg: str,
            args: ta.Sequence[ta.Any],
            kwargs: ta.Mapping[str, ta.Any],
            exc_info: ExceptionInfo | None,
            extra: ta.Mapping[str, ta.Any],
            frame_correction: int,
    ) -> None: ...

    def call_handlers(self, record: LogRecord) -> None: ...

    def process_record(self, record: LogRecord) -> None: ...


class Logger(RecordDispatcher, LoggerMixin):
    pass


class LoggerGroup:
    loggers: list[Logger]
    level: Level
    disabled: bool
    processor: ta.Callable[[LogRecord], None] | None

    def add_logger(self, logger: Logger) -> None: ...
    def remove_logger(self, logger: Logger) -> None: ...

    def process_record(self, record: LogRecord) -> None: ...

    def enable(self, force: bool = False) -> None: ...
    def disable(self, force: bool = False) -> None: ...


class Processor:
    def process(self, record: LogRecord) -> None: ...


class Handler:
    blackhole: bool
    level_name: str

    level: Level
    formatter: ta.Callable[[LogRecord, 'Handler'], ta.Any] | None
    filter: ta.Callable[[LogRecord], bool] | None
    bubble: bool

    def format(self, record: LogRecord) -> ta.Any: ...

    def should_handle(self, record: LogRecord) -> bool: ...

    def handle(self, record: LogRecord) -> None: ...

    def emit(self, record: LogRecord) -> None: ...

    def emit_batch(
            self,
            records: ta.Sequence[LogRecord],
            reason: ta.Literal['buffer', 'escalation', 'group'],
    ) -> None: ...

    def close(self) -> None: ...

    def handle_error(self, record: LogRecord, exc_info: ExceptionInfo) -> None: ...


class Lock:
    def acquire(self) -> None: ...
    def release(self) -> None: ...


class StreamHandler(Handler, ta.ContextManager):
    encoding: str | None
    lock: Lock

    def ensure_stream_is_open(self) -> None: ...

    def close(self) -> None: ...

    def flush(self) -> None: ...

    def encode(self, msg: ta.Any) -> str: ...

    def write(self, item: ta.Any) -> None: ...

    def emit(self, record: LogRecord) -> None: ...

    def should_flush(self) -> bool: ...


def _main():
    logbook.StreamHandler(sys.stdout).push_application()
    logbook.warn('This is a warning')


if __name__ == '__main__':
    _main()
