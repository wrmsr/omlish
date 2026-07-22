# ruff: noqa: UP006 UP007 UP045
# @om-lite
import typing as ta


Bytes = ta.Union[bytes, bytearray]  # ta.TypeAlias

BytesLike = ta.Union[Bytes, memoryview]  # ta.TypeAlias


##


BYTES_TYPES: ta.Tuple[ta.Union[ta.Type[bytes], ta.Type[bytearray]], ...] = (
    bytes,
    bytearray,
)

BYTES_LIKE_TYPES: ta.Tuple[ta.Union[ta.Type[bytes], ta.Type[bytearray], ta.Type[memoryview]], ...] = (
    *BYTES_TYPES,
    memoryview,
)


##


def bytes_like_to_bytes(bl: BytesLike, /) -> Bytes:
    if isinstance(bl, BYTES_TYPES):
        return bl

    return memoryview_to_bytes(bl)  # type: ignore[arg-type]


def bytes_like_to_bytes_strict(bl: BytesLike, /) -> bytes:
    if isinstance(bl, bytes):
        return bl

    if isinstance(bl, bytearray):
        return bytes(bl)

    return memoryview_to_bytes_strict(bl)


#


def memoryview_to_bytes(mv: memoryview, /) -> Bytes:
    if (mv.c_contiguous and ((ot := type(obj := mv.obj)) is bytes or ot is bytearray or isinstance(obj, BYTES_TYPES)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
        return obj  # type: ignore[return-value]

    return mv.tobytes()


def memoryview_to_bytes_strict(mv: memoryview, /) -> bytes:
    if (mv.c_contiguous and ((ot := type(obj := mv.obj)) is bytes or isinstance(obj, bytes)) and len(mv) == len(obj)):  # type: ignore[arg-type]  # noqa
        return obj  # type: ignore[return-value]

    return mv.tobytes()
