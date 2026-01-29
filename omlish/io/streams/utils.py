# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

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

    #

    @staticmethod
    def can_bytes(obj: ta.Any) -> bool:
        return isinstance(obj, ByteStreamBuffers._CAN_CONVERT_TYPES)

    @staticmethod
    def _to_bytes(obj: ta.Any) -> bytes:
        if isinstance(obj, memoryview):
            return obj.tobytes()

        elif isinstance(obj, ByteStreamBufferView):
            return obj.tobytes()

        elif isinstance(obj, ByteStreamBufferLike):
            return b''.join(bytes(mv) for mv in obj.segments())

        else:
            raise TypeError(obj)

    @staticmethod
    def to_bytes(obj: ta.Any) -> bytes:
        if isinstance(obj, bytes):
            return obj

        elif isinstance(obj, bytearray):
            return bytes(obj)

        else:
            return ByteStreamBuffers._to_bytes(obj)

    @staticmethod
    def to_bytes_or_bytearray(obj: ta.Any) -> ta.Union[bytes, bytearray]:
        if isinstance(obj, (bytes, bytearray)):
            return obj

        else:
            return ByteStreamBuffers._to_bytes(obj)

    #

    # @staticmethod
    # def can_byte_stream_buffer(obj: ta.Any) -> bool:
    #     return isinstance(obj, ByteStreamBuffers._CAN_CONVERT_TYPES)

    # @staticmethod
    # def to_byte_stream_buffer(obj: ta.Any) -> ByteStreamBuffer:
    #     if isinstance(obj, ByteStreamBuffer):
    #         return obj
    #
    #     elif isinstance(obj, ByteStreamBufferLike):
    #         return obj

    #

    @staticmethod
    def bytes_len(obj: ta.Any) -> int:
        if isinstance(obj, (bytes, bytearray, memoryview)):
            return len(obj)

        elif isinstance(obj, ByteStreamBufferLike):
            return sum(len(mv) for mv in obj.segments())

        else:
            # Not bytes-like
            return 0

    #

    @staticmethod
    def iter_segments(obj: ta.Any) -> ta.Iterator[memoryview]:
        if isinstance(obj, memoryview):
            yield obj

        elif isinstance(obj, (bytes, bytearray)):
            yield memoryview(obj)

        elif isinstance(obj, ByteStreamBufferLike):
            yield from obj.segments()

        else:
            raise TypeError(obj)
