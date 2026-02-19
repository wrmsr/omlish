# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ...lite.namespaces import NamespaceClass
from .types import ByteStreamBuffer
from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView


##


class ByteStreamBuffers(NamespaceClass):
    @staticmethod
    def memoryview_to_bytes(mv: memoryview, /) -> bytes:
        if (((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray))) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()

    ##

    _CAN_CONVERT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        bytes,
        bytearray,
        memoryview,
        ByteStreamBufferLike,
    )

    @classmethod
    def can_bytes(cls, obj: ta.Any, /) -> bool:
        return type(obj) in (cts := cls._CAN_CONVERT_TYPES) or isinstance(obj, cts)

    #

    @classmethod
    @ta.overload
    def buffer_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def buffer_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> bytes:
        ...

    @classmethod
    def buffer_to_bytes(cls, obj, or_none=False, /):
        if type(obj) is memoryview or isinstance(obj, memoryview):
            return cls.memoryview_to_bytes(obj)

        elif isinstance(obj, ByteStreamBufferView):
            return obj.tobytes()

        elif isinstance(obj, ByteStreamBufferLike):
            return b''.join(bytes(mv) for mv in obj.segments())

        elif or_none:
            return None

        else:
            raise TypeError(obj)

    #

    @classmethod
    @ta.overload
    def any_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def any_to_bytes(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> bytes:
        ...

    @classmethod
    def any_to_bytes(cls, obj, or_none=False, /):
        if (ot := type(obj)) is bytes:
            return obj
        elif ot is bytearray:
            return bytes(obj)

        elif isinstance(obj, bytes):
            return obj
        elif isinstance(obj, bytearray):
            return bytes(obj)

        else:
            return cls.buffer_to_bytes(obj, or_none)  # noqa

    #

    @classmethod
    @ta.overload
    def any_to_bytes_or_bytearray(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Union[bytes, bytearray, None]:
        ...

    @classmethod
    @ta.overload
    def any_to_bytes_or_bytearray(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> ta.Union[bytes, bytearray]:  # noqa
        ...

    @classmethod
    def any_to_bytes_or_bytearray(cls, obj, or_none=False, /):
        if (ot := type(obj)) is bytes or ot is bytearray or isinstance(obj, (bytes, bytearray)):
            return obj

        else:
            return cls.buffer_to_bytes(obj, or_none)  # noqa

    #

    @classmethod
    @ta.overload
    def bytes_len(cls, obj: ta.Any, or_none: ta.Literal[True], /) -> ta.Optional[int]:
        ...

    @classmethod
    @ta.overload
    def bytes_len(cls, obj: ta.Any, or_none: ta.Literal[False] = False, /) -> int:
        ...

    @classmethod
    def bytes_len(cls, obj, or_none=False):
        if cls.can_bytes(obj):
            return len(obj)

        elif or_none:
            return None

        else:
            raise TypeError(obj)

    ##

    @staticmethod
    def iter_segments(obj: ta.Any, /) -> ta.Iterator[memoryview]:
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

    @staticmethod
    def split(buf: ByteStreamBuffer, sep: bytes, /, *, final: bool = False) -> ta.List[ByteStreamBufferView]:
        out: ta.List[ByteStreamBufferView] = []
        while (i := buf.find(sep)) >= 0:
            out.append(buf.split_to(i + 1))
        if final and len(buf):
            out.append(buf.split_to(len(buf)))
        return out
