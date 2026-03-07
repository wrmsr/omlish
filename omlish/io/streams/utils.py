# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ...lite.namespaces import NamespaceClass
from .types import BytesLike
from .types import ByteStreamBuffer
from .types import ByteStreamBufferLike
from .types import ByteStreamBufferView


CanByteStreamBuffer = ta.Union[BytesLike, 'ByteStreamBufferLike']  # ta.TypeAlias


##


class ByteStreamBuffers(NamespaceClass):
    _BYTES_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        bytes,
        bytearray,
    )

    _BYTES_LIKE_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        *_BYTES_TYPES,
        memoryview,
    )

    _CAN_CONVERT_TYPES: ta.ClassVar[ta.Tuple[type, ...]] = (
        *_BYTES_LIKE_TYPES,
        ByteStreamBufferLike,
    )

    #

    @classmethod
    def can_bytes(cls, obj: ta.Any, /) -> bool:
        return type(obj) in (cts := cls._CAN_CONVERT_TYPES) or isinstance(obj, cts)

    #

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[True],
            or_none: ta.Literal[True],
    ) -> ta.Optional[bytes]:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[True],
            or_none: ta.Literal[False] = False,
    ) -> bytes:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[False] = False,
            or_none: ta.Literal[True],
    ) -> ta.Union[bytes, bytearray, None]:
        ...

    @classmethod
    @ta.overload
    def to_bytes(
            cls,
            obj: ta.Any,
            /, *,
            strict: ta.Literal[False] = False,
            or_none: ta.Literal[False] = False,
    ) -> ta.Union[bytes, bytearray]:
        ...

    @classmethod
    def to_bytes(
            cls,
            obj,
            /, *,
            strict=False,
            or_none=False,
    ):
        """
        Returns a non-shared version of the given object. If a possibly shared memoryview is acceptable, use
        `iter_segments`.
        """

        if strict:
            if (ot := type(obj)) is bytes or isinstance(obj, bytes):
                return obj

            elif ot is bytearray:
                return bytes(obj)

            elif isinstance(obj, memoryview):
                return cls.memoryview_to_bytes_strict(obj)

        else:
            if (ot := type(obj)) is bytes or ot is bytearray or isinstance(obj, cls._BYTES_TYPES):
                return obj

            elif isinstance(obj, memoryview):
                return cls.memoryview_to_bytes(obj)

        if isinstance(obj, ByteStreamBufferView):
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

    #

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

    #

    @staticmethod
    def split(buf: ByteStreamBuffer, sep: bytes, /, *, final: bool = False) -> ta.List[ByteStreamBufferView]:
        out: ta.List[ByteStreamBufferView] = []
        while (i := buf.find(sep)) >= 0:
            out.append(buf.split_to(i + 1))
        if final and len(buf):
            out.append(buf.split_to(len(buf)))
        return out

    #

    @classmethod
    def memoryview_to_bytes(cls, mv: memoryview, /) -> ta.Union[bytes, bytearray]:
        if (((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, cls._BYTES_TYPES)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()

    @staticmethod
    def memoryview_to_bytes_strict(mv: memoryview, /) -> bytes:
        if (((ot := type(obj := mv.obj)) is bytes or isinstance(obj, bytes)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
            return obj  # type: ignore[return-value]

        return mv.tobytes()
