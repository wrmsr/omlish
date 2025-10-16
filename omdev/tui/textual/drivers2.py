import threading
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    from textual.driver import Driver


##


class PendingWritesDriverMixin:
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self._pending_primary_buffer_writes: list[str] = []

    def queue_primary_buffer_write(self, *s: str) -> None:
        self._pending_primary_buffer_writes.extend(s)

    def write(self, data: str) -> None:
        if (pw := self._pending_primary_buffer_writes):
            data = ''.join([*pw, data])
            pw.clear()
        super().write(data)  # type: ignore


_PENDING_WRITES_DRIVER_CLASSES_LOCK = threading.RLock()
_PENDING_WRITES_DRIVER_CLASSES: dict[type['Driver'], type['Driver']] = {}


def get_pending_writes_driver_class(cls: type['Driver']) -> type['Driver']:
    if issubclass(cls, PendingWritesDriverMixin):
        return cls  # noqa

    try:
        return _PENDING_WRITES_DRIVER_CLASSES[cls]
    except KeyError:
        pass

    with _PENDING_WRITES_DRIVER_CLASSES_LOCK:
        try:
            return _PENDING_WRITES_DRIVER_CLASSES[cls]
        except KeyError:
            pass

        cls = _PENDING_WRITES_DRIVER_CLASSES[cls] = lang.new_type(  # noqa
            f'PendingWrites{cls.__name__}',
            (PendingWritesDriverMixin, cls),
            {},
        )

    return cls  # noqa
