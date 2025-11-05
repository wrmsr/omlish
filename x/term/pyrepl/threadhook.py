import threading
import traceback
import types
import typing as ta


if ta.TYPE_CHECKING:
    from .readers.reader import Reader


##


class ExceptHookArgs(ta.Protocol):
    @property
    def exc_type(self) -> type[BaseException]: ...

    @property
    def exc_value(self) -> BaseException | None: ...

    @property
    def exc_traceback(self) -> types.TracebackType | None: ...

    @property
    def thread(self) -> threading.Thread | None: ...


class ShowExceptions(ta.Protocol):
    def __call__(self) -> int: ...

    def add(self, s: str) -> None: ...


@ta.final
class _ExceptHookHandler:
    def __init__(self, reader: 'Reader') -> None:
        self._reader = reader

        self._lock: threading.Lock = threading.Lock()
        self._messages: list[str] = []

    def show(self) -> int:
        count = 0

        with self._lock:
            if not self._messages:
                return 0

            self._reader.restore()

            for tb in self._messages:
                count += 1
                if tb:
                    print(tb)

            self._messages.clear()
            self._reader.scheduled_commands.append('ctrl-c')
            self._reader.prepare()

        return count

    def add(self, s: str) -> None:
        with self._lock:
            self._messages.append(s)

    def exception(self, args: ExceptHookArgs) -> None:
        lines = traceback.format_exception(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            colorize=self._reader.can_colorize,
        )  # type: ignore[call-overload]

        pre = f'\nException in {args.thread.name}:\n' if args.thread else '\n'

        tb = pre + ''.join(lines)
        self.add(tb)

    def __call__(self) -> None:
        self.show()


def install_threading_hook(reader: 'Reader') -> None:
    handler = _ExceptHookHandler(reader)
    reader.threading_hook = handler
    threading.excepthook = handler.exception
