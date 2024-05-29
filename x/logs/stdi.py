import logging  # noqa
import types  # noqa
import typing as ta  # noqa

from omlish import logs


ExceptionInfo: ta.TypeAlias = tuple[type[BaseException], BaseException, types.TracebackType]


class LogRecord:
    name: str
    msg: str
    args: tuple
    levelname: str
    levelno: int
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


def _main():
    logs.configure_standard_logging(logging.INFO)
    try:
        raise ValueError('barf')
    except Exception:
        logging.info('hi', stack_info=True, exc_info=True)


if __name__ == '__main__':
    _main()
