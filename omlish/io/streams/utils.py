# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .types import ByteStreamBuffer
from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView


##


class ByteStreamBuffers:
    _CAN_CONVERT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        bytes,
        bytearray,
        memoryview,
        ByteStreamBufferLike,
    )

    @staticmethod
    def can_bytes(obj: ta.Any) -> bool:
        return type(obj) in (cts := ByteStreamBuffers._CAN_CONVERT_TYPES) or isinstance(obj, cts)

    #

    @staticmethod
    def memoryview_to_bytes(mv: memoryview) -> bytes:
        if (((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray))) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()

    @staticmethod
    def buffer_to_bytes(obj: ta.Any) -> bytes:
        if type(obj) is memoryview or isinstance(obj, memoryview):
            return ByteStreamBuffers.memoryview_to_bytes(obj)

        elif isinstance(obj, ByteStreamBufferView):
            return obj.tobytes()

        elif isinstance(obj, ByteStreamBufferLike):
            return b''.join(bytes(mv) for mv in obj.segments())

        else:
            raise TypeError(obj)

    @staticmethod
    def any_to_bytes(obj: ta.Any) -> bytes:
        if (ot := type(obj)) is bytes:
            return obj
        elif ot is bytearray:
            return bytes(obj)

        elif isinstance(obj, bytes):
            return obj
        elif isinstance(obj, bytearray):
            return bytes(obj)

        else:
            return ByteStreamBuffers.buffer_to_bytes(obj)

    @staticmethod
    def any_to_bytes_or_bytearray(obj: ta.Any) -> ta.Union[bytes, bytearray]:
        if (ot := type(obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray)):
            return obj

        else:
            return ByteStreamBuffers.buffer_to_bytes(obj)

    #

    @staticmethod
    def bytes_len(obj: ta.Any) -> int:
        if ByteStreamBuffers.can_bytes(obj):
            return len(obj)

        else:
            # Not bytes-like
            return 0

    #

    @staticmethod
    def iter_segments(obj: ta.Any) -> ta.Iterator[memoryview]:
        if (ot := type(obj)) is memoryview:
            yield obj
        elif ot is bytes or ot is bytearray:
            yield memoryview(obj)

        elif isinstance(obj, memoryview):
            yield obj
        elif isinstance(obj, (bytes, bytearray)):
            yield memoryview(obj)

        elif isinstance(obj, ByteStreamBufferLike):
            yield from obj.segments()

        else:
            raise TypeError(obj)

    #

    @staticmethod
    def split(buf: ByteStreamBuffer, sep: bytes, *, final: bool = False) -> ta.List[ByteStreamBufferView]:
        out: ta.List[ByteStreamBufferView] = []
        while (i := buf.find(sep)) >= 0:
            out.append(buf.split_to(i + 1))
        if final and len(buf):
            out.append(buf.split_to(len(buf)))
        return out
