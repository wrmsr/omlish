#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-generated
# @omlish-amalg-output ../../../../omlish/io/streams/_amalg.py
# @omlish-git-diff-omit
# ruff: noqa: UP006 UP007 UP036 UP045
import abc
import io
import sys
import time
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


def __omlish_amalg__():  # noqa
    return dict(
        src_files=[
            dict(path='errors.py', sha1='67ca85fd8741b5bfefe76c872ce1c30c18fab06f'),
            dict(path='../../lite/abstract.py', sha1='a2fc3f3697fa8de5247761e9d554e70176f37aac'),
            dict(path='types.py', sha1='6ae05b5486ac8eb1f2667d415aad0cde3c962df4'),
            dict(path='base.py', sha1='67ae88ffabae21210b5452fe49c9a3e01ca164c5'),
            dict(path='framing.py', sha1='7c004117cdd9e3ef93137e1b5562fb75af0ef2ef'),
            dict(path='reading.py', sha1='7631635c46ab4b40bcaeb7c506cf15cb2d529a40'),
            dict(path='utils.py', sha1='26621e9a464d6ce6e662f457c70288b6ee71aa7b'),
            dict(path='direct.py', sha1='6c04ad9249a8536ff1ccf7760e299ea34180502f'),
            dict(path='scanning.py', sha1='5d4cf0776463a6f675ca74ca87637133b78b51a2'),
            dict(path='adapters.py', sha1='1a6c209490fa78947a607101e20169a5e135847b'),
            dict(path='linear.py', sha1='dbee5a728aabbc22df49e5b31afc71b2b5dac988'),
            dict(path='segmented.py', sha1='5a24346389644caac91c25e9d2ccbe76b26a71a6'),
            dict(path='_amalg.py', sha1='4511d6a6f9ae80585eea1c68980df5323ef0ef14'),
        ],
    )


########################################


# ../../lite/abstract.py
T = ta.TypeVar('T')

# types.py
BytesLike = ta.Union[bytes, bytearray, memoryview]  # ta.TypeAlias


########################################
# ../errors.py


##


class ByteStreamBufferError(Exception):
    pass


#


class NeedMoreDataByteStreamBufferError(ByteStreamBufferError):
    """
    Raised when an operation cannot complete because insufficient bytes are currently buffered.

    This is intentionally distinct from EOF: it means "try again after feeding more bytes".
    """


#


class LimitByteStreamBufferError(ValueError, ByteStreamBufferError):
    """
    Base class for buffer/framing limit violations.

    Subclasses inherit from ValueError so existing tests expecting ValueError continue to pass.
    """


class BufferTooLargeByteStreamBufferError(LimitByteStreamBufferError):
    """
    Buffered data exceeded a configured cap without finding a boundary that would allow progress.

    Typically indicates an unframed stream, a missing delimiter, or an upstream not enforcing limits.
    """


class FrameTooLargeByteStreamBufferError(LimitByteStreamBufferError):
    """A single decoded frame (payload before its boundary delimiter/length) exceeded a configured max size."""


#


class StateByteStreamBufferError(RuntimeError, ByteStreamBufferError):
    """
    Base class for invalid buffer state transitions (e.g., coalescing while a reservation is outstanding).

    Subclasses inherit from RuntimeError so existing tests expecting RuntimeError continue to pass.
    """


class OutstandingReserveByteStreamBufferError(StateByteStreamBufferError):
    """A reserve() is outstanding; an operation requiring stable storage cannot proceed."""


class NoOutstandingReserveByteStreamBufferError(StateByteStreamBufferError):
    """commit() was called without a preceding reserve()."""


########################################
# ../../../lite/abstract.py


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))


def compute_abstract_methods(cls: type) -> ta.FrozenSet[str]:
    # ~> https://github.com/python/cpython/blob/f3476c6507381ca860eec0989f53647b13517423/Modules/_abc.c#L358

    # Stage 1: direct abstract methods

    abstracts = {
        a
        # Get items as a list to avoid mutation issues during iteration
        for a, v in list(cls.__dict__.items())
        if is_abstract_method(v)
    }

    # Stage 2: inherited abstract methods

    for base in cls.__bases__:
        # Get __abstractmethods__ from base if it exists
        if (base_abstracts := getattr(base, _ABSTRACT_METHODS_ATTR, None)) is None:
            continue

        # Iterate over abstract methods in base
        for key in base_abstracts:
            # Check if this class has an attribute with this name
            try:
                value = getattr(cls, key)
            except AttributeError:
                # Attribute not found in this class, skip
                continue

            # Check if it's still abstract
            if is_abstract_method(value):
                abstracts.add(key)

    return frozenset(abstracts)


def update_abstracts(cls: ta.Type[T], *, force: bool = False) -> ta.Type[T]:
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts = compute_abstract_methods(cls)
    setattr(cls, _ABSTRACT_METHODS_ATTR, abstracts)
    return cls


#


class AbstractTypeError(TypeError):
    pass


_FORCE_ABSTRACT_ATTR = '__forceabstract__'


class Abstract:
    """
    Different from, but interoperable with, abc.ABC / abc.ABCMeta:

     - This raises AbstractTypeError during class creation, not instance instantiation - unless Abstract or abc.ABC are
       explicitly present in the class's direct bases.
     - This will forbid instantiation of classes with Abstract in their direct bases even if there are no
       abstractmethods left on the class.
     - This is a mixin, not a metaclass.
     - As it is not an ABCMeta, this does not support virtual base classes. As a result, operations like `isinstance`
       and `issubclass` are ~7x faster.
     - It additionally enforces a base class order of (Abstract, abc.ABC) to preemptively prevent common mro conflicts.

    If not mixed-in with an ABCMeta, it will update __abstractmethods__ itself.
    """

    __slots__ = ()

    __abstractmethods__: ta.ClassVar[ta.FrozenSet[str]] = frozenset()

    #

    def __forceabstract__(self):
        raise TypeError

    # This is done manually, rather than through @abc.abstractmethod, to mask it from static analysis.
    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        setattr(
            cls,
            _FORCE_ABSTRACT_ATTR,
            getattr(Abstract, _FORCE_ABSTRACT_ATTR) if Abstract in cls.__bases__ else False,
        )

        super().__init_subclass__(**kwargs)

        if not (Abstract in cls.__bases__ or abc.ABC in cls.__bases__):
            if ams := compute_abstract_methods(cls):
                amd = {
                    a: mcls
                    for mcls in cls.__mro__[::-1]
                    for a in ams
                    if a in mcls.__dict__
                }

                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([
                                *([m] if (m := getattr(c, '__module__')) else []),
                                getattr(c, '__qualname__', getattr(c, '__name__')),
                            ] if c is not None else '?'),
                            a,
                        ])
                        for a in ams
                        for c in [amd.get(a)]
                    ])),
                )

        xbi = (Abstract, abc.ABC)  # , ta.Generic ?
        bis = [(cls.__bases__.index(b), b) for b in xbi if b in cls.__bases__]
        if bis != sorted(bis):
            raise TypeError(
                f'Abstract subclass {cls.__name__} must have proper base class order of '
                f'({", ".join(getattr(b, "__name__") for b in xbi)}), got: '
                f'({", ".join(getattr(b, "__name__") for _, b in sorted(bis))})',
            )

        if not isinstance(cls, abc.ABCMeta):
            update_abstracts(cls, force=True)


########################################
# ../types.py


##


class ByteStreamBufferLike(Abstract):
    @ta.final
    def __bool__(self) -> bool:
        raise TypeError('Do not use bool() for ByteStreamBufferLike, use len().')

    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Return the number of readable bytes.

        This is expected to be O(1). Many drivers and codecs use `len(buf)` in tight loops to decide whether more data
        is needed before attempting to parse a frame.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def peek(self) -> memoryview:
        """
        Return a contiguous, read-only `memoryview` of the first available bytes.

        This is the "next chunk" fast-path: for segmented views, the returned memoryview may represent only the first
        segment (and thus may be shorter than `len(self)`), but it must be non-copying. This is the fast-path for codecs
        that can parse headers from an initial contiguous region.

        The returned view should be treated as ephemeral: callers must assume it may be invalidated by subsequent buffer
        mutations (advance/write/reserve/commit), depending on the implementation.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def segments(self) -> ta.Sequence[memoryview]:
        """
        Return the readable contents as an ordered sequence of non-copying `memoryview` segments.

        This method is required because efficient operations in pure Python typically depend on delegating work to
        CPython's optimized implementations for searching/slicing within contiguous regions. By exposing
        already-contiguous segments, the buffer enables implementations of `find/rfind` and higher-level framing to
        avoid Python-level per-byte iteration.

        The returned segments must:
          - collectively represent exactly the readable bytes, in order
          - be 1-D, byte-oriented views (itemsize 1)
          - be non-copying views of the underlying storage
          - be non-empty - lack of data is represented by returning no segments, not a empty segments

        Callers must assume that the returned views may be invalidated by subsequent mutations of the originating
        buffer/view (e.g., advancing, writing, reserving, committing), depending on the implementation's rules.
        """

        raise NotImplementedError


class ByteStreamBufferView(ByteStreamBufferLike, Abstract):
    """
    A read-only, possibly non-contiguous view of bytes.

    This is the result type of operations like `ByteStreamBuffer.split_to()`: it represents a *logical* byte sequence
    without requiring a copy. A `ByteStreamBufferView` is intentionally minimal: it is not a general-purpose container
    API, not a random-access sequence, and not intended for arbitrary indexing/slicing-heavy use.

    `ByteStreamBufferView` exists to make copy boundaries explicit:
      - Use `segments()` / `peek()` to access data without copying.
      - Use `tobytes()` (or `bytes(view)`) to intentionally materialize a contiguous `bytes` object.

    Implementations may be backed by one or many `memoryview` segments; the semantics are defined as if all readable
    bytes were concatenated in order.
    """

    @abc.abstractmethod
    def tobytes(self) -> bytes:
        """
        Materialize this view as a contiguous `bytes` object (copying).

        This is the explicit copy boundary: callers should prefer `peek()` / `segments()` for zero-copy-ish access when
        feasible, and use `tobytes()` only when a contiguous owned `bytes` is required.
        """

        raise NotImplementedError


class ByteStreamBuffer(ByteStreamBufferLike, Abstract):
    """
    An incremental, consumption-oriented byte accumulator intended for protocol parsing.

    A `ByteStreamBuffer` is a *stream buffer*: bytes are appended by a driver/transport and then consumed by codecs via
    peeking, searching, splitting, and advancing-without forcing repeated concatenation or reallocation. It is
    explicitly designed to support segmented storage (to avoid "a huge buffer pinned by a tiny tail") and to enable
    low-copy pipeline-style decoding (Netty/Tokio-inspired).

    What it is for:
      - buffering raw bytes between I/O and protocol codecs,
      - framing (delimiters/length-prefixed) using split/advance,
      - efficient searching over buffered bytes using C-accelerated primitives via `memoryview` segments.

    What it is *not* for:
      - a general-purpose replacement for `bytes`/`bytearray`,
      - a `collections.abc.Sequence` or random-access container abstraction,
      - arbitrary indexing/slicing-heavy workloads (use `bytes`/`bytearray`/`memoryview` directly).

    `ByteStreamBuffer` deliberately exposes `memoryview` at its boundary. This is foundational: it allows both immutable
    (`bytes`) and mutable (`bytearray`) internal storage to be viewed in O(1) without copying. It also avoids relying
    on `io.BytesIO` as a core backing store: while `BytesIO.getbuffer()` can expose a view, exported views pin the
    underlying buffer against resizing, which makes it awkward as a general-purpose buffer substrate.

    Semantics note:
      Many methods describe behavior in terms of the *conceptual concatenation* of readable bytes, even if the buffer
      is physically segmented. This is what "stream-correct" means here: results must be correct regardless of how the
      buffered bytes are chunked internally.
    """

    @abc.abstractmethod
    def advance(self, n: int, /) -> None:
        """
        Consume (discard) exactly `n` readable bytes from the front of the buffer.

        This operation must not copy remaining bytes unnecessarily. For segmented buffers, this typically adjusts a head
        offset and drops exhausted segments.

        Implementations must raise if `n` is negative or greater than `len(self)`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def split_to(self, n: int, /) -> ByteStreamBufferView:
        """
        Split off and return a read-only view of the first `n` readable bytes, consuming them from this buffer.

        This is the core "low-copy framing" primitive:
          - codecs can `split_to(frame_len)` to obtain a view of an entire frame without copying,
          - then immediately continue parsing subsequent frames from the remaining bytes.

        Implementations should strive for O(1) or amortized O(1) behavior, returning a view that references underlying
        segments rather than materializing a new contiguous `bytes`.

        Implementations must raise if `n` is negative or greater than `len(self)`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def coalesce(self, n: int, /) -> memoryview:
        """
        Ensure the first `n` readable bytes are available contiguously and return a view of them.

        Semantics:
          - Non-consuming: does not advance.
          - May restructure internal segments (content-preserving) to make the prefix contiguous.
          - Returns a read-only-ish `memoryview` (callers must not mutate readable bytes).

        Copying behavior:
          - If `peek()` already exposes >= n contiguous bytes, this is zero-copy.
          - Otherwise, it copies exactly the first `n` bytes into a new contiguous segment and rewrites the internal
            segment list so that segment[0] contains that prefix.

        Reserve interaction:
          - Disallowed while an outstanding reservation exists, since reserve() hands out a view that must not be
            invalidated by internal reshaping.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        """
        Find the first occurrence of `sub` within the readable bytes and return its offset, or -1 if not found.

        This operation is "stream-correct": it must behave as if searching within the conceptual concatenation of all
        readable bytes, even if the buffer is physically segmented. In particular, matches that span segment boundaries
        must be detected.

        `start` and `end` are offsets into the readable region, matching the semantics of `bytes.find()`:
          - `start` defaults to 0 (the beginning of readable bytes),
          - `end` defaults to `len(self)`.

        Rationale for being part of the core interface:
          In pure Python, higher-level codecs cannot efficiently implement correct cross-segment searching byte-by-byte.
          Keeping `find` near the owning storage allows implementations to exploit contiguous segments and CPython's
          optimized search within each segment while still providing correct stream semantics.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        """
        Find the last occurrence of `sub` within the readable bytes and return its offset, or -1 if not found.

        This operation is also stream-correct and matches `bytes.rfind()` semantics for `start`/`end`, interpreted as
        offsets into the readable region of this buffer.
        """

        raise NotImplementedError


class MutableByteStreamBuffer(ByteStreamBuffer, Abstract):
    """
    A writable `ByteStreamBuffer`: supports appending bytes and (optionally) reserving writable space.

    `MutableByteStreamBuffer` is the primary target for drivers/transports feeding data into protocol pipelines, and for
    encoders building outbound byte sequences. It intentionally does not imply any particular I/O model (blocking,
    asyncio, custom reactors); it is simply the mutable byte substrate.

    Implementations may be linear (single `bytearray` + indices), segmented (multiple chunks), or adaptive.
    """

    @abc.abstractmethod
    def write(self, data: BytesLike, /) -> None:
        """
        Append `data` to the end of the readable region (after any existing unread bytes).

        Implementations should avoid needless copying; e.g., segmented buffers may store large `bytes` chunks directly,
        while linear buffers may copy into a `bytearray`.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def reserve(self, n: int, /) -> memoryview:
        """
        Reserve writable space for at least `n` bytes and return a writable `memoryview` into that space.

        This method exists to support "close to the metal" drivers that can fill buffers directly (e.g., `recv_into`,
        `readinto`) without allocating temporary `bytes` objects.

        The returned view represents capacity that is not yet part of the readable region. The caller must write into
        some prefix of the view and then call `commit(written)` to make those bytes readable.

        Implementations should document their rules regarding outstanding reservations; a simple and robust rule is:
          - only one active reservation may exist at a time,
          - mutations that would reallocate storage are forbidden while a reservation is outstanding.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, n: int, /) -> None:
        """
        Commit `n` bytes from the most recent reservation, making them readable.

        Conceptually, `reserve()` may provide more capacity than the caller actually uses; `commit(n)` "shrinks" that
        over-reservation by only publishing the first `n` bytes as readable.

        Implementations must validate:
          - that a reservation is outstanding,
          - that `0 <= n <= reserved_length`.

        After commit, the reservation is considered consumed; subsequent reads and searches must include the committed
        bytes as part of the readable region.
        """

        raise NotImplementedError


########################################
# ../base.py


##


class BaseByteStreamBufferLike(ByteStreamBufferLike, Abstract):
    def _norm_slice(self, start: int, end: ta.Optional[int]) -> ta.Tuple[int, int]:
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s
        return s, e


########################################
# ../framing.py


##


class LongestMatchDelimiterByteStreamFramer:
    """
    A delimiter-based framing codec that supports *overlapping* delimiters with longest-match semantics.

    This is intentionally decoupled from any I/O model: it operates purely on a `ByteStreamBuffer`-like object
    (providing `__len__`, `find`, `split_to`, `advance`, and `segments`/`peek`).

    Key property:
      Given overlapping delimiters like [b'\\r', b'\\r\\n'], this codec will *not* emit a frame ending at '\\r' unless
      it can prove the next byte is not '\\n' (or the stream is finalized).

    Implementation note:
      This codec relies on `ByteStreamBuffer.find(...)` being stream-correct and C-accelerated over the buffer's
      underlying contiguous segments. In pure Python it is usually better to keep searching near the storage layer than
      to re-implement scanning byte-by-byte in higher-level codecs.
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        dl = list(delims)
        if not dl:
            raise ValueError('no delimiters')
        if any(not isinstance(d, (bytes, bytearray)) for d in dl):
            raise TypeError(delims)
        if any(not d for d in dl):
            raise ValueError('empty delimiter')

        self._delims = tuple(bytes(d) for d in dl)
        self._keep_ends = keep_ends
        self._max_size = max_size

        # Sort by length descending for "choose longest at same start".
        self._delims_by_len = tuple(sorted(self._delims, key=len, reverse=True))

        # Build prefix relationships for overlap deferral. For each short delimiter, store longer delimiters that start
        # with it.
        pref: ta.Dict[bytes, ta.List[bytes]] = {}
        for d in self._delims:
            for e in self._delims:
                if d is e:
                    continue
                if len(e) > len(d) and e.startswith(d):
                    pref.setdefault(d, []).append(e)
        for k, vs in list(pref.items()):
            pref[k] = sorted(vs, key=len, reverse=True)
        self._prefix_longer = pref

        self._max_delim_len = max(len(d) for d in self._delims)

    @ta.overload
    def decode(
            self,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
            include_delims: ta.Literal[True],
    ) -> ta.List[ta.Tuple[ByteStreamBufferView, bytes]]:
        ...

    @ta.overload
    def decode(
            self,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
            include_delims: ta.Literal[False] = False,
    ) -> ta.List[ByteStreamBufferView]:
        ...

    def decode(
            self,
            buf,
            *,
            final=False,
            include_delims=False,
    ):
        """
        Consume as many complete frames as possible from `buf` and return them as views.

        - Frames are produced without copying (via `buf.split_to(...)`) when possible.
        - The delimiter is consumed from the buffer; it may be retained on the frame if `keep_ends=True`.
        - If `final=True`, the codec will not defer on overlapping delimiter prefixes at the end of the buffer.

        Raises:
          - BufferTooLargeByteStreamBufferError if no delimiter is present and the buffered prefix exceeds max_size.
          - FrameTooLargeByteStreamBufferError if the next frame payload (bytes before delimiter) exceeds max_size.

        Note on `max_size`:
          `max_size` is enforced as a limit on the *current* frame (bytes before the next delimiter). If the buffer
          contains bytes for a subsequent frame that already exceed `max_size`, this codec will only raise when it would
          otherwise need to make progress on that oversized frame. Concretely: if this call already emitted at least one
          frame, it will return those frames rather than raising immediately on trailing oversized data, leaving the
          remaining bytes buffered.
        """

        out: ta.List[ta.Any] = []

        while True:
            hit = self._find_next_delim(buf)
            if hit is None:
                if self._max_size is not None and len(buf) > self._max_size and not out:
                    raise BufferTooLargeByteStreamBufferError('buffer exceeded max_size without delimiter')
                return out

            pos, delim = hit

            if self._max_size is not None and pos > self._max_size:
                raise FrameTooLargeByteStreamBufferError('frame exceeded max_size')

            if not final and self._should_defer(buf, pos, delim):
                return out

            if self._keep_ends:
                frame = buf.split_to(pos + len(delim))
            else:
                frame = buf.split_to(pos)
                buf.advance(len(delim))

            if include_delims:
                out.append((frame, delim))
            else:
                out.append(frame)

    def _find_next_delim(self, buf: ByteStreamBuffer) -> ta.Optional[ta.Tuple[int, bytes]]:
        """
        Return (pos, delim) for the earliest delimiter occurrence. If multiple delimiters occur at the same position,
        choose the longest matching delimiter.
        """

        ln = len(buf)
        if not ln:
            return None

        best_pos = None  # type: ta.Optional[int]
        best_delim = None  # type: ta.Optional[bytes]

        # First pass: find the earliest position of any delimiter (cheap, uses buf.find).
        for d in self._delims:
            i = buf.find(d, 0, None)
            if i == -1:
                continue
            if best_pos is None or i < best_pos:
                best_pos = i
                best_delim = d
                if not best_pos:
                    # Can't beat position 0; still need to choose longest at this position.
                    pass
            elif i == best_pos and best_delim is not None and len(d) > len(best_delim):
                best_delim = d

        if best_pos is None or best_delim is None:
            return None

        # Second pass: at that position, choose the longest delimiter that actually matches there. (We can't just rely
        # on "which delimiter found it first" when overlaps exist.)
        pos = best_pos
        for d in self._delims_by_len:
            if pos + len(d) > ln:
                continue
            if buf.find(d, pos, pos + len(d)) == pos:
                return pos, d

        # Shouldn't happen: best_pos came from some delimiter occurrence.
        return pos, best_delim

    def _should_defer(self, buf: ByteStreamBuffer, pos: int, matched: bytes) -> bool:
        """
        Return True if we must defer because a longer delimiter could still match starting at `pos` but we don't yet
        have enough bytes to decide.

        We only defer when:
          - the current match ends at the end of the currently buffered bytes, and
          - there exists some longer delimiter that has `matched` as a prefix, and
          - the buffered bytes from pos match the available prefix of that longer delimiter.
        """

        ln = len(buf)
        endpos = pos + len(matched)
        if endpos != ln:
            return False

        longer = self._prefix_longer.get(matched)
        if not longer:
            return False

        avail = ln - pos
        for d2 in longer:
            if avail >= len(d2):
                # If we had enough bytes, we'd have matched d2 in _find_next_delim.
                continue
            # Check whether buffered bytes match the prefix of d2 that we have available.
            # Use stream-correct find on the prefix.
            prefix = d2[:avail]
            if buf.find(prefix, pos, pos + avail) == pos:
                return True

        return False


########################################
# ../reading.py


##


class ByteStreamBufferReader:
    def __init__(self, buf: ByteStreamBuffer) -> None:
        super().__init__()

        self._buf = buf

    #

    def _coalesce_exact(self, n: int) -> memoryview:
        """
        Return a contiguous view of exactly `n` readable bytes, or raise NeedMoreDataByteStreamBufferError.

        Uses `buf.coalesce(n)` to avoid per-byte Python work and to keep copying close to the buffer backend.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        mv = self._buf.coalesce(n)
        if len(mv) < n:
            # Defensive: coalesce contract should provide >= n when len(buf) >= n.
            raise NeedMoreDataByteStreamBufferError
        return mv[:n]

    #

    def peek_u8(self) -> int:
        """Peek an unsigned 8-bit integer without consuming."""

        mv = self._coalesce_exact(1)
        return mv[0]

    def read_u8(self) -> int:
        """Read and consume an unsigned 8-bit integer."""

        v = self.peek_u8()
        self._buf.advance(1)
        return v

    def peek_u16_be(self) -> int:
        """Peek an unsigned 16-bit big-endian integer without consuming."""

        mv = self._coalesce_exact(2)
        return int.from_bytes(mv, 'big', signed=False)

    def read_u16_be(self) -> int:
        """Read and consume an unsigned 16-bit big-endian integer."""

        v = self.peek_u16_be()
        self._buf.advance(2)
        return v

    def peek_u16_le(self) -> int:
        """Peek an unsigned 16-bit little-endian integer without consuming."""

        mv = self._coalesce_exact(2)
        return int.from_bytes(mv, 'little', signed=False)

    def read_u16_le(self) -> int:
        """Read and consume an unsigned 16-bit little-endian integer."""

        v = self.peek_u16_le()
        self._buf.advance(2)
        return v

    def peek_u32_be(self) -> int:
        """Peek an unsigned 32-bit big-endian integer without consuming."""

        mv = self._coalesce_exact(4)
        return int.from_bytes(mv, 'big', signed=False)

    def read_u32_be(self) -> int:
        """Read and consume an unsigned 32-bit big-endian integer."""

        v = self.peek_u32_be()
        self._buf.advance(4)
        return v

    def peek_u32_le(self) -> int:
        """Peek an unsigned 32-bit little-endian integer without consuming."""

        mv = self._coalesce_exact(4)
        return int.from_bytes(mv, 'little', signed=False)

    def read_u32_le(self) -> int:
        """Read and consume an unsigned 32-bit little-endian integer."""

        v = self.peek_u32_le()
        self._buf.advance(4)
        return v

    #

    def peek_exact(self, n: int, /) -> memoryview:
        """
        Return a contiguous view of exactly `n` readable bytes without consuming.

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        mv = self._buf.coalesce(n)
        if len(mv) < n:
            raise NeedMoreDataByteStreamBufferError
        return mv[:n]

    def take(self, n: int, /) -> ByteStreamBufferView:
        """
        Consume and return a `ByteStreamBufferView`-like object representing exactly `n` bytes.

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        if n < 0:
            raise ValueError(n)
        if len(self._buf) < n:
            raise NeedMoreDataByteStreamBufferError
        return self._buf.split_to(n)

    def read_bytes(self, n: int, /) -> bytes:
        """
        Consume exactly `n` bytes and return them as a contiguous `bytes` object (copy boundary).

        Raises NeedMoreDataByteStreamBufferError if fewer than `n` bytes are currently buffered.
        """

        v = self.take(n)
        return v.tobytes()


########################################
# ../utils.py


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


########################################
# ../direct.py


##


class BaseDirectByteStreamBufferLike(BaseByteStreamBufferLike, Abstract):
    def __init__(self, data: BytesLike) -> None:
        super().__init__()

        self._data = data
        if isinstance(data, memoryview):
            self._mv_ = data
        else:
            self._b_ = data

    _mv_: memoryview
    _b_: ta.Union[bytes, bytearray]

    def _mv(self) -> memoryview:
        try:
            return self._mv_
        except AttributeError:
            pass

        self._mv_ = mv = memoryview(self._b_)
        return mv

    def _b(self) -> ta.Union[bytes, bytearray]:
        try:
            return self._b_
        except AttributeError:
            pass

        mv = self._mv_
        obj = mv.obj
        if isinstance(obj, (bytes, bytearray)) and len(mv) == len(obj):
            b = obj
        else:
            b = bytes(mv)
        self._b_ = b
        return b


class DirectByteStreamBufferView(BaseDirectByteStreamBufferLike, ByteStreamBufferView):
    def __len__(self) -> int:
        return len(self._data)

    def peek(self) -> memoryview:
        return self._mv()

    def segments(self) -> ta.Sequence[memoryview]:
        return (self._mv(),) if len(self._data) else ()

    def tobytes(self) -> bytes:
        if type(b := self._b()) is bytes:
            return b
        return bytes(b)


class DirectByteStreamBuffer(BaseDirectByteStreamBufferLike, ByteStreamBuffer):
    """
    A read-only ByteStreamBuffer that wraps existing bytes without copying.

    This is a lightweight, zero-copy wrapper around bytes/bytearray/memoryview that provides the full
    ByteStreamBuffer interface (find, rfind, split_to, advance, coalesce) without mutation capabilities.

    Strengths:
      - Zero-copy construction from existing data
      - Always contiguous (coalesce is trivial)
      - Fast find/rfind delegating to optimized bytes methods
      - Simple implementation with minimal overhead

    Use cases:
      - Parsing fixed/immutable data (HTTP requests, protocol messages)
      - Using framers/codecs on data already in memory
      - Avoiding buffer allocation/copying overhead when mutation isn't needed

    Important notes:
      - If constructed from a bytearray, the underlying data could still be mutated externally. This is by design -
        we're wrapping directly, not defensively copying.
      - This is a read-only buffer - it does not implement MutableByteStreamBuffer (no write/reserve/commit).
      - All views returned from split_to() remain valid as they reference the original underlying data.

    Example:
        >>> data = b'GET /path HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n'
        >>> buf = DirectByteStreamBuffer(data)
        >>> pos = buf.find(b'\\r\\n\\r\\n')
        >>> headers = buf.split_to(pos)
        >>> print(headers.tobytes())
        b'GET /path HTTP/1.1\\r\\nHost: example.com'
    """

    def __init__(self, data: BytesLike) -> None:
        super().__init__(data)

        self._rpos = 0

    def __len__(self) -> int:
        return len(self._data) - self._rpos

    def peek(self) -> memoryview:
        mv = self._mv()
        if self._rpos >= len(mv):
            return memoryview(b'')
        return mv[self._rpos:]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self.peek()
        return (mv,) if len(mv) else ()

    def advance(self, n: int, /) -> None:
        if n < 0 or n > len(self):
            raise ValueError(n)
        self._rpos += n

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        if not self._rpos and n == len(self._data):
            self._rpos += n
            return DirectByteStreamBufferView(self._data)

        mv = self._mv()
        view = mv[self._rpos:self._rpos + n]
        self._rpos += n
        return DirectByteStreamBufferView(view)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        if not sub:
            return start

        b = self._b()
        idx = b.find(sub, self._rpos + start, self._rpos + end)
        return (idx - self._rpos) if idx >= 0 else -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        if not sub:
            return end

        b = self._b()
        idx = b.rfind(sub, self._rpos + start, self._rpos + end)
        return (idx - self._rpos) if idx >= 0 else -1

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return memoryview(b'')

        # Always contiguous - just return the requested slice
        mv = self._mv()
        return mv[self._rpos:self._rpos + n]


##


_EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW = DirectByteStreamBufferView(b'')


def empty_byte_stream_buffer_view() -> ByteStreamBufferView:
    return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW


########################################
# ../scanning.py


##


class ScanningByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A MutableByteStreamBuffer wrapper that caches negative-find progress to avoid repeated rescans in trickle scenarios.

    It is intentionally conservative:
      - It only caches progress for the default find range (start==0, end is None).
      - It only caches *negative* results (i.e., "-1"): once a match is found, caching is not updated, to preserve the
        property that repeated `find(sub)` on an unchanged buffer yields the same answer.

    This is designed to help framing-style code that repeatedly does:
      - buf.write(...small...)
      - buf.find(delim)
      - (not found) repeat
    """

    def __init__(self, buf) -> None:
        super().__init__()

        self._buf = buf
        self._scan_from_by_sub: dict[bytes, int] = {}

    #

    def __len__(self) -> int:
        return len(self._buf)

    def peek(self) -> memoryview:
        return self._buf.peek()

    def segments(self) -> ta.Sequence[memoryview]:
        return self._buf.segments()

    #

    def advance(self, n: int, /) -> None:
        self._buf.advance(n)
        self._adjust_for_consume(n)

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        v = self._buf.split_to(n)
        self._adjust_for_consume(n)
        return v

    def coalesce(self, n: int, /) -> memoryview:
        return self._buf.coalesce(n)

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        if start != 0 or end is not None:
            return self._buf.find(sub, start, end)

        sub_len = len(sub)
        if sub_len <= 0:
            return self._buf.find(sub, start, end)

        scan_from = self._scan_from_by_sub.get(sub, 0)

        # Allow overlap so a match spanning old/new boundary is discoverable.
        overlap = sub_len - 1
        eff_start = scan_from - overlap
        if eff_start < 0:
            eff_start = 0

        i = self._buf.find(sub, eff_start, None)
        if i < 0:
            self._scan_from_by_sub[sub] = len(self._buf)

        return i

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # rfind isn't the typical trickle hot-path; delegate.
        return self._buf.rfind(sub, start, end)

    #

    def write(self, data: BytesLike, /) -> None:
        self._buf.write(data)

    def reserve(self, n: int, /) -> memoryview:
        return self._buf.reserve(n)

    def commit(self, n: int, /) -> None:
        self._buf.commit(n)

    #

    def _adjust_for_consume(self, n: int) -> None:
        if not self._scan_from_by_sub:
            return

        if n <= 0:
            return

        # Only front-consumption exists in this buffer model.
        for k, v in list(self._scan_from_by_sub.items()):
            nv = v - n
            if nv <= 0:
                self._scan_from_by_sub.pop(k, None)
            else:
                self._scan_from_by_sub[k] = nv


########################################
# ../adapters.py


##


class ByteStreamBufferReaderAdapter:
    """
    Adapter: ByteStreamBuffer -> file-like reader methods (`read1`, `read`, `readall`).

    This adapter is policy-driven for how it behaves when insufficient bytes are available. The core buffer is
    intentionally non-blocking; blocking behavior (if desired) must be provided via a `fill` callback that supplies more
    bytes into the buffer.

    `policy`:
      - 'raise': raise NeedMoreDataByteStreamBufferError if fewer than `n` bytes are available (for n >= 0).
      - 'return_partial': return whatever is available (possibly b'') up to `n`.
      - 'block': repeatedly call `fill()` until satisfied or until `fill()` signals EOF.

    `fill`:
      - Callable that writes more bytes into the underlying MutableByteStreamBuffer and returns:
          * True  -> made progress / more data may be available
          * False -> EOF / no more data will arrive
      - Only used when policy == 'block'.

    This adapter exists for interop with legacy code that expects file-like objects, but the core design remains
    independent from `io` and blocking semantics.
    """

    def __init__(
            self,
            buf: ByteStreamBuffer,
            *,
            policy: ta.Literal['raise', 'return_partial', 'block'] = 'raise',
            fill: ta.Optional[ta.Callable[[], bool]] = None,
            block_sleep: ta.Union[ta.Callable[[], None], float, None] = None,
    ) -> None:
        super().__init__()

        self._buf = buf
        self._policy = policy
        self._fill = fill
        self._block_sleep = block_sleep

        if self._policy == 'block' and self._fill is None:
            raise ValueError('policy=block requires fill')

    def _on_block(self) -> None:
        if (bs := self._block_sleep) is None:
            return
        elif callable(bs):
            bs()
        else:
            time.sleep(bs)

    def read1(self, n: int = -1, /) -> bytes:
        return self.read(n)

    def read(self, n: int = -1, /) -> bytes:
        buf = self._buf

        if n is None or n < 0:
            return self.readall()

        if not n:
            return b''

        while True:
            ln = len(buf)
            if ln >= n:
                v = buf.split_to(n)
                return v.tobytes()

            if self._policy == 'return_partial':
                if not ln:
                    return b''
                v = buf.split_to(ln)
                return v.tobytes()

            if self._policy == 'raise':
                raise NeedMoreDataByteStreamBufferError

            # block
            if not ta.cast('ta.Callable[[], bool]', self._fill)():
                # EOF
                if not ln:
                    return b''
                v = buf.split_to(ln)
                return v.tobytes()

            self._on_block()

    def readall(self) -> bytes:
        buf = self._buf
        parts: ta.List[bytes] = []

        while True:
            ln = len(buf)
            if ln:
                v = buf.split_to(ln)
                parts.append(v.tobytes())
                continue

            if self._policy == 'block':
                if not ta.cast('ta.Callable[[], bool]', self._fill)():
                    break
                self._on_block()
                continue

            break

        return b''.join(parts)


class ByteStreamBufferWriterAdapter:
    """
    Adapter: file-like writer sink <- ByteStreamBuffer / bytes-like.

    This is intentionally small and dumb: it exists to bridge into code expecting a `.write(...)` method on an object.

    If given a ByteStreamBufferView-like object, it writes segment-by-segment to avoid materializing copies when the
    sink can accept multiple writes efficiently.
    """

    def __init__(self, f: ta.Any) -> None:
        super().__init__()

        self._f = f

    def write(self, data: ta.Any) -> int:
        f = self._f

        if isinstance(data, (bytes, bytearray, memoryview)):
            b = data.tobytes() if isinstance(data, memoryview) else bytes(data)
            return ta.cast(int, f.write(b))

        if isinstance(data, ByteStreamBufferLike):
            total = 0
            for mv in data.segments():
                total += ta.cast(int, f.write(bytes(mv)))
            return total

        if isinstance(data, ByteStreamBufferView):
            b = data.tobytes()
            return ta.cast(int, f.write(b))

        raise TypeError(data)


##


class BytesIoByteStreamBuffer(MutableByteStreamBuffer):
    """
    ByteStreamBuffer/MutableByteStreamBuffer implementation backed by `io.BytesIO`, using `getbuffer()`.

    This exists primarily for interoperability with code that already produces/consumes `BytesIO`, and to demonstrate
    how `getbuffer()` can expose a non-copying `memoryview` of internal storage.

    Caveat (important):
      - Any exported `memoryview` from `BytesIO.getbuffer()` can pin the BytesIO against resizing.
      - If a caller holds onto a view and we attempt to grow/resize internally, `BytesIO` may raise `BufferError`.

    This backing is therefore best suited for controlled scenarios; it is *not* the recommended default buffer backend
    for applications (segmented/bytearray backends are more predictable).
    """

    def __init__(
            self,
            *,
            compaction_threshold: int = 1 << 16,
    ) -> None:
        super().__init__()

        self._compaction_threshold = compaction_threshold

        self._bio = io.BytesIO()
        self._rpos = 0

        # reserve/commit state
        self._resv: ta.Optional[bytearray] = None
        self._resv_len = 0

    def __len__(self) -> int:
        return self._bio.getbuffer().nbytes - self._rpos

    def peek(self) -> memoryview:
        mv = self._bio.getbuffer()
        return mv[self._rpos:]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self._bio.getbuffer()
        seg = mv[self._rpos:]
        return (seg,) if len(seg) else ()

    def advance(self, n: int, /) -> None:
        if n < 0 or n > len(self):
            raise ValueError(n)
        self._rpos += n
        # Optional compaction heuristic: if we've consumed a lot, rebuild a smaller BytesIO.
        # This may fail if someone holds a getbuffer() view (BufferError).
        if (
                self._rpos and
                self._rpos >= self._compaction_threshold and
                self._rpos >= (self._bio.getbuffer().nbytes // 2)
        ):
            try:
                remaining = self._bio.getbuffer()[self._rpos:].tobytes()
                self._bio = io.BytesIO(remaining)
                self._rpos = 0
            except BufferError as e:  # noqa
                raise

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > len(self):
            raise ValueError(n)
        mv = self._bio.getbuffer()
        out = mv[self._rpos:self._rpos + n]
        self._rpos += n
        return DirectByteStreamBufferView(out)

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        try:
            self._bio.seek(0, io.SEEK_END)
            self._bio.write(data)
        except BufferError as e:  # noqa
            raise

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._resv is not None:
            raise RuntimeError('outstanding reserve')
        b = bytearray(n)
        self._resv = b
        self._resv_len = n
        return memoryview(b)

    def commit(self, n: int, /) -> None:
        if self._resv is None:
            raise RuntimeError('no outstanding reserve')
        if n < 0 or n > self._resv_len:
            raise ValueError(n)
        b = self._resv
        self._resv = None
        self._resv_len = 0
        if n:
            self.write(memoryview(b)[:n])

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return memoryview(b'')
        # BytesIO is always contiguous, just return the requested slice
        mv = self._bio.getbuffer()
        return mv[self._rpos:self._rpos + n]

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # Normalize start/end to valid range
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s

        if not sub:
            return s

        # Convert to bytes for searching (memoryview doesn't have find method)
        b = bytes(self._bio.getbuffer())
        idx = b.find(sub, self._rpos + s, self._rpos + e)
        return (idx - self._rpos) if idx >= 0 else -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        # Normalize start/end to valid range
        s, e, _ = slice(start, end, 1).indices(len(self))
        if e < s:
            e = s

        if not sub:
            return e

        # Convert to bytes for searching (memoryview doesn't have rfind method)
        b = bytes(self._bio.getbuffer())
        idx = b.rfind(sub, self._rpos + s, self._rpos + e)
        return (idx - self._rpos) if idx >= 0 else -1


########################################
# ../linear.py


##


class LinearByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A simple contiguous (bytearray-backed) MutableByteStreamBuffer implementation.

    Strengths:
      - Fast `find/rfind` and contiguous peeking.
      - Efficient reserve/commit (safe against exported-memoryview resizing hazards).

    Tradeoffs:
      - `split_to` returns a stable view by copying the split bytes into an owned `bytes` object. (A truly zero-copy
        split view would require pinning the underlying bytearray against compaction.)
      - Compaction is best-effort: if the backing bytearray is pinned by exported memoryviews, compaction will be
        skipped and the buffer will remain correct but may retain memory.
    """

    def __init__(
            self,
            *,
            max_bytes: ta.Optional[int] = None,
            initial_capacity: int = 0,
            compact_threshold: int = 1 << 16,
    ) -> None:
        super().__init__()

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if initial_capacity < 0:
            raise ValueError(initial_capacity)
        if self._max_bytes is not None and initial_capacity > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        if compact_threshold < 0:
            raise ValueError(compact_threshold)
        self._compact_threshold = int(compact_threshold)

        # Diagnostics (best-effort compaction behavior)
        self.compaction_attempts = 0
        self.compaction_successes = 0
        self.compaction_skipped_exports = 0

        # Pre-size the backing store to encourage fewer resizes/copies on trickle-y writes. We immediately clear so
        # readable length remains 0.
        if initial_capacity:
            self._ba = bytearray(initial_capacity)
            self._ba.clear()
        else:
            self._ba = bytearray()

    _rpos = 0
    _wpos = 0

    _resv_start: ta.Optional[int] = None
    _resv_len = 0

    _resv_buf: bytearray

    def __len__(self) -> int:
        return self._wpos - self._rpos

    def peek(self) -> memoryview:
        if self._rpos == self._wpos:
            return memoryview(b'')
        return memoryview(self._ba)[self._rpos:self._wpos]

    def segments(self) -> ta.Sequence[memoryview]:
        mv = self.peek()
        return (mv,) if len(mv) else ()

    def _check_no_reserve(self) -> None:
        if self._resv_start is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

    def write(self, data: BytesLike, /) -> None:
        self._check_no_reserve()
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        elif isinstance(data, bytearray):
            data = bytes(data)

        bl = len(data)

        if self._max_bytes is not None and len(self) + bl > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        # If buffer is logically empty but backing store might still be large (e.g. compaction skipped),
        # keep indices reset and just append.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            # Best-effort shrink on empty: may be pinned, so ignore failure.
            self._try_clear_if_empty()

        self._ba.extend(data)
        self._wpos += bl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._resv_start is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        # Do NOT reserve by extending the backing bytearray and returning a view into it: a live exported memoryview
        # pins the bytearray against resizing, and commit() would need to shrink unused reservation (or otherwise
        # reshape), which would raise BufferError.
        #
        # Instead, reserve returns a view of a temporary bytearray, and commit() appends only what was written.
        b = bytearray(n)
        self._resv_start = 0
        self._resv_len = n
        self._resv_buf = b
        return memoryview(b)

    def commit(self, n: int, /) -> None:
        if self._resv_start is None:
            raise NoOutstandingReserveByteStreamBufferError('no outstanding reserve')
        if n < 0 or n > self._resv_len:
            raise ValueError(n)

        b = self._resv_buf
        self._resv_start = None
        self._resv_len = 0
        del self._resv_buf

        if not n:
            return

        if self._max_bytes is not None and len(self) + n > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        # Append only what was written.
        self.write(memoryview(b)[:n])

    def advance(self, n: int, /) -> None:
        self._check_no_reserve()
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return

        self._rpos += n

        # Best-effort compaction (may skip if backing store is pinned by exported memoryviews).
        self.compact()

        # Fully consumed: reset indices and attempt to clear backing store best-effort.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            self._try_clear_if_empty()

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        self._check_no_reserve()
        if n < 0 or n > len(self):
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        # Copy out the split prefix to keep the view stable even if the underlying buffer compacts.
        b = bytes(memoryview(self._ba)[self._rpos:self._rpos + n])
        self._rpos += n

        # If we consumed everything, reset best-effort; otherwise allow compaction policy to handle later.
        if self._rpos == self._wpos:
            self._rpos = 0
            self._wpos = 0
            self._try_clear_if_empty()

        return DirectByteStreamBufferView(memoryview(b))

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)
        if not sub:
            return start
        i = self._ba.find(sub, self._rpos + start, self._rpos + end)
        return -1 if i < 0 else (i - self._rpos)

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)
        if not sub:
            return end
        i = self._ba.rfind(sub, self._rpos + start, self._rpos + end)
        return -1 if i < 0 else (i - self._rpos)

    def coalesce(self, n: int, /) -> memoryview:
        self._check_no_reserve()
        if n < 0:
            raise ValueError(n)
        if n > len(self):
            raise ValueError(n)
        if not n:
            return memoryview(b'')
        # Always contiguous for the readable prefix.
        return memoryview(self._ba)[self._rpos:self._rpos + n]

    def compact(
            self,
            *,
            threshold: ta.Optional[int] = None,
            min_fraction: float = 0.5,
            force: bool = False,
    ) -> bool:
        """
        Best-effort compaction to avoid "huge buffer pinned by small tail".

        Returns True if compaction happened, False otherwise.

        Compaction attempts to drop the consumed prefix of the backing bytearray by resizing it. If the bytearray is
        pinned by exported memoryviews, Python raises BufferError; in that case compaction is skipped (buffer remains
        correct) and the skip is recorded in diagnostics.

        Args:
          threshold: minimum consumed prefix size (bytes) required before compaction is considered. Defaults to the
                     instance's configured compact threshold (64KiB by default).
          min_fraction: require consumed prefix to be at least this fraction of the backing 'written' size. Defaults to
                        0.5 (i.e., consumed >= half of written region).
          force: if True, ignore heuristic checks and attempt compaction whenever `_rpos > 0`.

        Notes:
          - Compaction is disallowed while a reserve is outstanding.
          - Compaction is an optimization only; semantics do not depend on it.
        """

        self._check_no_reserve()

        if threshold is None:
            threshold = self._compact_threshold
        else:
            threshold = int(threshold)

        if not force:
            if self._rpos <= 0:
                return False
            if self._rpos < threshold:
                return False
            if self._wpos <= 0:
                return False
            if self._rpos < int(self._wpos * float(min_fraction)):
                return False
        else:
            if self._rpos <= 0:
                return False

        self.compaction_attempts += 1

        try:
            del self._ba[:self._rpos]
        except BufferError:
            self.compaction_skipped_exports += 1
            return False

        self._wpos -= self._rpos
        self._rpos = 0
        self.compaction_successes += 1
        return True

    def _try_clear_if_empty(self) -> None:
        """
        Best-effort clear of backing store when logically empty.

        If the backing store is pinned by exported memoryviews, clear will raise BufferError.
        In that case we keep the backing store allocated (correctness preserved) and move on.
        """

        if self._rpos != 0 or self._wpos != 0:
            return
        if not self._ba:
            return

        try:
            self._ba.clear()
        except BufferError:
            # Keep storage; callers wanted deterministic correctness over reclamation.
            pass


########################################
# ../segmented.py


##


class SegmentedByteStreamBufferView(BaseByteStreamBufferLike, ByteStreamBufferView):
    """
    A read-only, possibly non-contiguous view over a sequence of byte segments.

    This is intended to be produced by `SegmentedByteStreamBuffer.split_to()` without copying.
    """

    def __init__(self, segs: ta.Sequence[memoryview]) -> None:
        super().__init__()

        self._segs = tuple(segs)
        for mv in self._segs:
            self._len += len(mv)

    _len = 0

    def __len__(self) -> int:
        return self._len

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')
        return self._segs[0]

    def segments(self) -> ta.Sequence[memoryview]:
        return self._segs

    def tobytes(self) -> bytes:
        if not self._segs:
            return b''
        if len(self._segs) == 1:
            return bytes(self._segs[0])
        return b''.join(bytes(mv) for mv in self._segs)


class SegmentedByteStreamBuffer(BaseByteStreamBufferLike, MutableByteStreamBuffer):
    """
    A segmented, consumption-oriented bytes buffer.

    Internally stores a list of `bytes`/`bytearray` segments plus a head offset. Exposes readable data as `memoryview`
    segments without copying.

    Optional "chunked writes":
      - If chunk_size > 0, small writes are accumulated into a lazily-allocated active bytearray "chunk" up to
        chunk_size.
      - Writes >= chunk_size are stored as their own segments (after flushing any active chunk).
      - On flush, the active chunk is kept as a bytearray segment iff it is at least `chunk_compact_threshold` full;
        otherwise it is materialized as bytes to avoid pinning a large capacity for tiny content.

    Reserve/commit:
      - If chunk_size > 0 and reserve(n) fits in the active chunk, the reservation is carved from the active chunk.
        Reserved bytes are not readable until commit().
      - If reserve(n) does not fit, the active chunk is flushed first.
      - If n <= chunk_size after flushing, the reservation is served from a new active chunk (so the remainder becomes
        the next active chunk).
      - If n > chunk_size, reserve allocates a dedicated buffer and on commit it is "closed" (it does not become the
        next active chunk).

    Important exported-view caveat:
      - reserve() returns a memoryview. As long as any exported memoryview exists, the underlying bytearray must not be
        resized, or Python will raise BufferError. Therefore the active chunk bytearray is *fixed capacity*
        (len==chunk_size) and we track "used" bytes separately, writing via slice assignment rather than extend().
    """

    def __init__(
            self,
            *,
            max_bytes: ta.Optional[int] = None,
            chunk_size: int = 0,
            chunk_compact_threshold: float = .25,
    ) -> None:
        super().__init__()

        self._segs: ta.List[ta.Union[bytes, bytearray]] = []

        self._max_bytes = None if max_bytes is None else int(max_bytes)

        if chunk_size < 0:
            raise ValueError(chunk_size)
        self._chunk_size = chunk_size

        if not (0.0 <= chunk_compact_threshold <= 1.0):
            raise ValueError(chunk_compact_threshold)
        self._chunk_compact_threshold = chunk_compact_threshold

        self._active: ta.Optional[bytearray] = None
        self._active_used = 0

    _head_off = 0
    _len = 0

    _reserved: ta.Optional[bytearray] = None
    _reserved_len = 0
    _reserved_in_active = False

    #

    def __len__(self) -> int:
        return self._len

    def _active_readable_len(self) -> int:
        if self._active is None:
            return 0
        if self._reserved_in_active and self._reserved is not None:
            tail = self._reserved_len
        else:
            tail = 0
        rl = self._active_used - tail
        return rl if rl > 0 else 0

    def peek(self) -> memoryview:
        if not self._segs:
            return memoryview(b'')

        s0 = self._segs[0]
        mv = memoryview(s0)
        if self._head_off:
            mv = mv[self._head_off:]

        if s0 is self._active:
            # Active is only meaningful by _active_used, not len(bytearray).
            rl = self._active_readable_len()
            if self._head_off >= rl:
                return memoryview(b'')
            mv = memoryview(self._active)[self._head_off:rl]
            return mv

        return mv

    def segments(self) -> ta.Sequence[memoryview]:
        if not self._segs:
            return ()

        out: ta.List[memoryview] = []

        last_i = len(self._segs) - 1
        for i, s in enumerate(self._segs):
            if s is self._active and i == last_i:
                # Active chunk: create fresh view with readable length.
                rl = self._active_readable_len()
                if not i:
                    # Active is also first segment; apply head_off.
                    if self._head_off >= rl:
                        continue
                    mv = memoryview(self._active)[self._head_off:rl]
                else:
                    if rl <= 0:
                        continue
                    mv = memoryview(self._active)[:rl]
            else:
                # Non-active segment.
                mv = memoryview(s)
                if not i and self._head_off:
                    mv = mv[self._head_off:]

            if len(mv):
                out.append(mv)

        return tuple(out)

    #

    def _ensure_active(self) -> bytearray:
        if self._chunk_size <= 0:
            raise RuntimeError('no active chunk without chunk_size')

        a = self._active
        if a is None:
            a = bytearray(self._chunk_size)  # fixed capacity
            self._segs.append(a)
            self._active = a
            self._active_used = 0

        return a

    def _flush_active(self) -> None:
        if (a := self._active) is None:
            return

        if self._reserved_in_active:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if (used := self._active_used) <= 0:
            if self._segs and self._segs[-1] is a:
                self._segs.pop()
            self._active = None
            self._active_used = 0
            return

        # If under threshold, always bytes() to avoid pinning.
        if self._chunk_size and (float(used) / float(self._chunk_size)) < self._chunk_compact_threshold:
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            self._segs[-1] = bytes(memoryview(a)[:used])

        else:
            # Try to shrink in-place to used bytes. If exported views exist, this can BufferError; fall back to bytes()
            # in that case.
            if not self._segs or self._segs[-1] is not a:
                raise RuntimeError('active not at tail')
            try:
                del a[used:]  # may raise BufferError if any exports exist
            except BufferError:
                self._segs[-1] = bytes(memoryview(a)[:used])

        self._active = None
        self._active_used = 0

    def write(self, data: BytesLike, /) -> None:
        if not data:
            return
        if isinstance(data, memoryview):
            data = data.tobytes()
        # elif isinstance(data, bytearray):
        #     pass
        # else:
        #     pass

        dl = len(data)

        if self._max_bytes is not None and self._len + dl > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        if self._chunk_size <= 0:
            self._segs.append(data)
            self._len += dl
            return

        if self._reserved_in_active:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if dl >= self._chunk_size:
            self._flush_active()
            self._segs.append(data)
            self._len += dl
            return

        a = self._ensure_active()
        if self._active_used + dl > self._chunk_size:
            self._flush_active()
            a = self._ensure_active()

        # Copy into fixed-capacity buffer; do not resize.
        memoryview(a)[self._active_used:self._active_used + dl] = data
        self._active_used += dl
        self._len += dl

    def reserve(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if self._reserved is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        if self._chunk_size <= 0:
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        if n > self._chunk_size:
            self._flush_active()
            b = bytearray(n)
            self._reserved = b
            self._reserved_len = n
            self._reserved_in_active = False
            return memoryview(b)

        # Ensure reservation fits in active; otherwise flush then create a new one.
        if self._active is not None and (self._active_used + n > self._chunk_size):
            self._flush_active()

        a = self._ensure_active()

        start = self._active_used
        # Reservation does not change _active_used (not readable until commit).
        self._reserved = a
        self._reserved_len = n
        self._reserved_in_active = True
        return memoryview(a)[start:start + n]

    def commit(self, n: int, /) -> None:
        if self._reserved is None:
            raise NoOutstandingReserveByteStreamBufferError('no outstanding reserve')
        if n < 0 or n > self._reserved_len:
            raise ValueError(n)

        if self._reserved_in_active:
            a = self._reserved
            self._reserved = None
            self._reserved_len = 0
            self._reserved_in_active = False

            if self._max_bytes is not None and self._len + n > self._max_bytes:
                raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

            if n:
                self._active_used += n
                self._len += n

            # Keep active for reuse.
            self._active = a
            return

        b = self._reserved
        self._reserved = None
        self._reserved_len = 0
        self._reserved_in_active = False

        if self._max_bytes is not None and self._len + n > self._max_bytes:
            raise BufferTooLargeByteStreamBufferError('buffer exceeded max_bytes')

        if not n:
            return

        if n == len(b):
            self._segs.append(b)
            self._len += n
        else:
            bb = bytes(memoryview(b)[:n])
            self._segs.append(bb)
            self._len += n

    #

    def advance(self, n: int, /) -> None:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if not n:
            return

        self._len -= n

        while n and self._segs:
            s0 = self._segs[0]

            if s0 is self._active:
                avail0 = self._active_readable_len() - self._head_off
            else:
                avail0 = len(s0) - self._head_off

            if avail0 <= 0:
                popped = self._segs.pop(0)
                if popped is self._active:
                    self._active = None
                    self._active_used = 0
                self._head_off = 0
                continue

            if n < avail0:
                self._head_off += n
                return

            n -= avail0
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        if n:
            raise RuntimeError(n)

    def split_to(self, n: int, /) -> ByteStreamBufferView:
        if n < 0 or n > self._len:
            raise ValueError(n)
        if not n:
            return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW

        out: ta.List[memoryview] = []
        rem = n

        while rem:
            if not self._segs:
                raise RuntimeError(rem)

            s0 = self._segs[0]

            if s0 is self._active:
                rl = self._active_readable_len()
                if self._head_off >= rl:
                    raise RuntimeError(rem)
                mv0 = memoryview(s0)[self._head_off:rl]
            else:
                mv0 = memoryview(s0)
                if self._head_off:
                    mv0 = mv0[self._head_off:]

            if rem < len(mv0):
                out.append(mv0[:rem])
                self._head_off += rem
                self._len -= n
                return byte_stream_buffer_view_from_segments(out)

            out.append(mv0)
            rem -= len(mv0)
            popped = self._segs.pop(0)
            if popped is self._active:
                self._active = None
                self._active_used = 0
            self._head_off = 0

        self._len -= n
        return byte_stream_buffer_view_from_segments(out)

    def coalesce(self, n: int, /) -> memoryview:
        if n < 0:
            raise ValueError(n)
        if n > self._len:
            raise ValueError(n)
        if not n:
            return memoryview(b'')

        if self._reserved is not None:
            raise OutstandingReserveByteStreamBufferError('outstanding reserve')

        mv0 = self.peek()
        if len(mv0) >= n:
            return mv0[:n]

        out = bytearray(n)
        w = 0

        new_segs: ta.List[ta.Union[bytes, bytearray]] = []

        seg_i = 0
        while w < n and seg_i < len(self._segs):
            s = self._segs[seg_i]
            off = self._head_off if not seg_i else 0

            seg_len = len(s) - off
            if s is self._active and seg_i == (len(self._segs) - 1):
                seg_len = self._active_readable_len() - off

            if seg_len <= 0:
                seg_i += 1
                continue

            take = n - w
            if take > seg_len:
                take = seg_len

            out[w:w + take] = memoryview(s)[off:off + take]
            w += take

            if take < seg_len:
                rem = s[off + take:off + seg_len]
                if rem:
                    new_segs.append(rem)
                seg_i += 1
                break

            seg_i += 1

        if seg_i < len(self._segs):
            new_segs.extend(self._segs[seg_i:])

        self._segs = [bytes(out), *new_segs]
        self._head_off = 0

        self._active = None
        self._active_used = 0

        return memoryview(self._segs[0])[:n]

    def _seg_readable_slice(
            self,
            si: int,
            s: ta.Union[bytes, bytearray],
            last_i: int,
    ) -> ta.Tuple[int, int]:
        """
        Compute the readable offset and length for segment at index si.

        Returns (offset, readable_len) where:
          - offset: byte offset into segment (head_off for si==0, else 0)
          - readable_len: number of readable bytes from offset (0 if segment empty/consumed)

        Handles head offset for first segment and active chunk readable length for last segment.
        """

        off = self._head_off if not si else 0
        seg_len = len(s) - off
        if s is self._active and si == last_i:
            seg_len = self._active_readable_len() - off
        return off, max(0, seg_len)

    def _seg_search_range(
            self,
            start: int,
            limit: int,
            m: int,
            seg_gs: int,
            seg_ge: int,
            seg_len: int,
    ) -> ta.Optional[ta.Tuple[int, int]]:
        """
        Compute local search range within a segment.

        Args:
            start: global start position (user-provided)
            limit: global limit (end - m, last valid position where match can start)
            m: pattern length
            seg_gs: segment global start position
            seg_ge: segment global end position
            seg_len: segment readable length

        Returns (local_start, local_end) if segment overlaps search range, else None.
          - local_start: offset within segment to start searching
          - local_end: offset within segment to end searching (exclusive)
        """

        # Check if segment overlaps search range
        if limit < seg_gs or start >= seg_ge:
            return None

        # Compute local start within segment
        ls = max(0, start - seg_gs)

        # Compute local end: can start match anywhere up to limit, need m bytes
        max_start_in_seg = limit - seg_gs
        end_search = min(max_start_in_seg + m, seg_len)

        # Validate range
        if ls >= end_search:
            return None

        return ls, end_search

    def find(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        m = len(sub)
        if m == 0:
            return start
        if end - start < m:
            return -1

        limit = end - m

        tail = b''
        tail_gstart = 0

        gpos = 0

        last_i = len(self._segs) - 1

        for si, s in enumerate(self._segs):
            off, seg_len = self._seg_readable_slice(si, s, last_i)
            if seg_len <= 0:
                continue

            seg_gs = gpos
            seg_ge = gpos + seg_len

            # Within-segment search
            search_range = self._seg_search_range(start, limit, m, seg_gs, seg_ge, seg_len)
            if search_range is not None:
                ls, end_search = search_range
                idx = s.find(sub, off + ls, off + end_search)
                if idx != -1:
                    return seg_gs + (idx - off)

            if m > 1 and tail:
                head_need = m - 1
                # Only read as many bytes as are actually available in this segment to avoid reading uninitialized data
                # from active chunks.
                head_avail = min(head_need, seg_len)
                if head_avail > 0:
                    head = s[off:off + head_avail]
                    comb = tail + head
                    j = comb.find(sub)
                    if j != -1 and j < len(tail) < j + m:
                        cand = tail_gstart + j
                        if start <= cand <= limit:
                            return cand

            if m > 1:
                take = m - 1
                if seg_len >= take:
                    tail = s[off + seg_len - take:off + seg_len]
                    tail_gstart = seg_ge - take
                else:
                    tail = (tail + s[off:off + seg_len])[-(m - 1):]
                    tail_gstart = seg_ge - len(tail)

            gpos = seg_ge

        return -1

    def rfind(self, sub: bytes, start: int = 0, end: ta.Optional[int] = None) -> int:
        start, end = self._norm_slice(start, end)

        m = len(sub)
        if m == 0:
            return end
        if end - start < m:
            return -1

        limit = end - m

        if not self._segs:
            return -1

        best = -1

        seg_ge = self._len
        prev_s: ta.Optional[ta.Union[bytes, bytearray]] = None
        prev_off = 0
        prev_seg_len = 0

        last_i = len(self._segs) - 1

        for si in range(len(self._segs) - 1, -1, -1):
            s = self._segs[si]
            off, seg_len = self._seg_readable_slice(si, s, last_i)
            if seg_len <= 0:
                continue

            seg_gs = seg_ge - seg_len

            # Within-segment search
            search_range = self._seg_search_range(start, limit, m, seg_gs, seg_ge, seg_len)
            if search_range is not None:
                ls, end_search = search_range
                idx = s.rfind(sub, off + ls, off + end_search)
                if idx != -1:
                    cand = seg_gs + (idx - off)
                    if cand > best:
                        best = cand

            if m > 1 and prev_s is not None:
                tail_need = m - 1
                if seg_len >= tail_need:
                    tail = s[off + seg_len - tail_need:off + seg_len]
                    tail_gstart = seg_ge - tail_need

                else:
                    tail_parts = [s[off:off + seg_len]]
                    tail_len = seg_len
                    for sj in range(si - 1, -1, -1):
                        if tail_len >= tail_need:
                            break

                        sj_s = self._segs[sj]
                        sj_off, sj_len = self._seg_readable_slice(sj, sj_s, last_i)
                        if sj_len <= 0:
                            continue

                        take = min(tail_need - tail_len, sj_len)
                        tail_parts.insert(0, sj_s[sj_off + sj_len - take:sj_off + sj_len])
                        tail_len += take

                    tail_combined = b''.join(tail_parts)
                    tail = tail_combined[-(m - 1):] if len(tail_combined) >= m - 1 else tail_combined
                    tail_gstart = seg_ge - len(tail)

                head_need = m - 1
                # Only read as many bytes as are actually available in prev segment to avoid reading uninitialized data
                # from active chunks.
                head_avail = min(head_need, prev_seg_len)
                if head_avail > 0:
                    head = prev_s[prev_off:prev_off + head_avail]
                else:
                    head = b''

                comb = tail + head
                j = comb.rfind(sub)
                if j != -1 and j < len(tail) < j + m:
                    cand = tail_gstart + j
                    if start <= cand <= limit and cand > best:
                        best = cand

            if best >= seg_gs:
                return best

            prev_s = s
            prev_off = off
            prev_seg_len = seg_len
            seg_ge = seg_gs

        return best


##


def byte_stream_buffer_view_from_segments(mvs: ta.Sequence[memoryview]) -> ByteStreamBufferView:
    if not mvs:
        return _EMPTY_DIRECT_BYTE_STREAM_BUFFER_VIEW
    elif len(mvs) == 1:
        return DirectByteStreamBufferView(mvs[0])
    else:
        return SegmentedByteStreamBufferView(mvs)


########################################
# _amalg.py


##
