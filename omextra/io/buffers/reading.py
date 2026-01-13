# @omlish-lite
import typing as ta

from .errors import NeedMoreData
from .types import BytesBuffer


##


def _coalesce_exact(buf: BytesBuffer, n: int) -> memoryview:
    """
    Return a contiguous view of exactly `n` readable bytes, or raise NeedMoreData.

    Uses `buf.coalesce(n)` to avoid per-byte Python work and to keep copying close to the buffer backend.
    """

    if n < 0:
        raise ValueError(n)
    if len(buf) < n:
        raise NeedMoreData
    mv = buf.coalesce(n)
    if len(mv) < n:
        # Defensive: coalesce contract should provide >= n when len(buf) >= n.
        raise NeedMoreData
    return mv[:n]


##


def peek_u8(buf: BytesBuffer) -> int:
    """Peek an unsigned 8-bit integer without consuming."""

    mv = _coalesce_exact(buf, 1)
    return mv[0]


def read_u8(buf: BytesBuffer) -> int:
    """Read and consume an unsigned 8-bit integer."""

    v = peek_u8(buf)
    buf.advance(1)
    return v


def peek_u16_be(buf: BytesBuffer) -> int:
    """Peek an unsigned 16-bit big-endian integer without consuming."""

    mv = _coalesce_exact(buf, 2)
    return int.from_bytes(mv, 'big', signed=False)


def read_u16_be(buf: BytesBuffer) -> int:
    """Read and consume an unsigned 16-bit big-endian integer."""

    v = peek_u16_be(buf)
    buf.advance(2)
    return v


def peek_u16_le(buf: BytesBuffer) -> int:
    """Peek an unsigned 16-bit little-endian integer without consuming."""

    mv = _coalesce_exact(buf, 2)
    return int.from_bytes(mv, 'little', signed=False)


def read_u16_le(buf: BytesBuffer) -> int:
    """Read and consume an unsigned 16-bit little-endian integer."""

    v = peek_u16_le(buf)
    buf.advance(2)
    return v


def peek_u32_be(buf: BytesBuffer) -> int:
    """Peek an unsigned 32-bit big-endian integer without consuming."""

    mv = _coalesce_exact(buf, 4)
    return int.from_bytes(mv, 'big', signed=False)


def read_u32_be(buf: BytesBuffer) -> int:
    """Read and consume an unsigned 32-bit big-endian integer."""

    v = peek_u32_be(buf)
    buf.advance(4)
    return v


def peek_u32_le(buf: BytesBuffer) -> int:
    """Peek an unsigned 32-bit little-endian integer without consuming."""

    mv = _coalesce_exact(buf, 4)
    return int.from_bytes(mv, 'little', signed=False)


def read_u32_le(buf: BytesBuffer) -> int:
    """Read and consume an unsigned 32-bit little-endian integer."""

    v = peek_u32_le(buf)
    buf.advance(4)
    return v


##


def peek_exact(buf: BytesBuffer, n: int, /) -> memoryview:
    """
    Return a contiguous view of exactly `n` readable bytes without consuming.

    Raises NeedMoreData if fewer than `n` bytes are currently buffered.
    """

    if n < 0:
        raise ValueError(n)
    if len(buf) < n:
        raise NeedMoreData
    mv = buf.coalesce(n)
    if len(mv) < n:
        raise NeedMoreData
    return mv[:n]


def take(buf: BytesBuffer, n: int, /) -> ta.Any:
    """
    Consume and return a `BytesView`-like object representing exactly `n` bytes.

    Raises NeedMoreData if fewer than `n` bytes are currently buffered.
    """

    if n < 0:
        raise ValueError(n)
    if len(buf) < n:
        raise NeedMoreData
    return buf.split_to(n)


def read_bytes(buf: BytesBuffer, n: int, /) -> bytes:
    """
    Consume exactly `n` bytes and return them as a contiguous `bytes` object (copy boundary).

    Raises NeedMoreData if fewer than `n` bytes are currently buffered.
    """

    v = take(buf, n)
    return ta.cast(bytes, v.tobytes())
