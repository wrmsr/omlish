# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from .errors import BufferTooLargeByteStreamBufferError
from .errors import FrameTooLargeByteStreamBufferError
from .types import ByteStreamBuffer
from .types import ByteStreamBufferView


##


class LongestMatchDelimiterByteStreamFrameDecoder:
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


##


class LengthFieldByteStreamFrameDecoder:
    """
    Decode length-prefixed frames from a BytesBuffer/MutableBytesBuffer.

    This is modeled after the common Netty pattern:
      total_frame_length = length_field_value + length_adjustment + length_field_end_offset
    where:
      length_field_end_offset = length_field_offset + length_field_length

    Parameters:
      - length_field_offset: byte offset of the length field from the start of the frame
      - length_field_length: length of the length field in bytes (1, 2, 4, or 8)
      - byteorder: 'big' or 'little'
      - length_adjustment: adjustment added to computed frame length (may be negative)
      - initial_bytes_to_strip: number of leading bytes to drop from the emitted frame (typically used to strip the
        length field and/or header from the delivered payload)
      - max_frame_length: maximum allowed total frame length (before stripping)

    Notes:
      - This decoder operates directly on the provided buffer and consumes bytes as frames are produced.
      - It relies on `buf.coalesce(n)` for efficient header parsing in pure Python.
      - It does not require async/await and is suitable for pipeline-style codecs.
    """

    def __init__(
            self,
            *,
            length_field_offset: int = 0,
            length_field_length: int = 4,
            byteorder: ta.Literal['little', 'big'] = 'big',
            length_adjustment: int = 0,
            initial_bytes_to_strip: int = 0,
            max_frame_length: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        if length_field_offset < 0:
            raise ValueError(length_field_offset)
        if length_field_length not in (1, 2, 4, 8):
            raise ValueError(length_field_length)
        if byteorder not in ('big', 'little'):
            raise ValueError(byteorder)
        if initial_bytes_to_strip < 0:
            raise ValueError(initial_bytes_to_strip)
        if max_frame_length is not None and max_frame_length < 0:
            raise ValueError(max_frame_length)

        self._off = int(length_field_offset)
        self._llen = int(length_field_length)
        self._byteorder = byteorder
        self._adj = int(length_adjustment)
        self._strip = int(initial_bytes_to_strip)
        self._max = None if max_frame_length is None else int(max_frame_length)

        self._end_off = self._off + self._llen

    def decode(self, buf: ByteStreamBuffer) -> ta.List[ByteStreamBufferView]:
        """
        Consume as many complete frames as possible from `buf` and return them as views.

        Returns:
          - list of BytesView-like objects (from `split_to`) representing each decoded frame

        Raises:
          - FrameTooLarge if a frame exceeds max_frame_length
          - BufferTooLarge if max_frame_length is set and the buffered unread prefix grows beyond it without making
            progress (defensive; rarely hit if upstream caps buffer growth)
        """

        out: ta.List[ta.Any] = []

        while True:
            # Need at least enough bytes to read the length field.
            if len(buf) < self._end_off:
                return out

            # Read header up through the length field contiguously.
            # IMPORTANT: don't keep exported memoryviews alive across buffer mutation.
            mv = buf.coalesce(self._end_off)
            if len(mv) < self._end_off:
                # Defensive: coalesce contract.
                return out

            # Copy just the length field bytes (1/2/4/8) so we can safely mutate the buffer afterward.
            lf_bytes = bytes(mv[self._off:self._end_off])
            # del mv

            length_val = int.from_bytes(lf_bytes, self._byteorder, signed=False)

            total_len = length_val + self._adj + self._end_off
            if total_len < 0:
                raise ValueError('negative frame length')

            if self._max is not None and total_len > self._max:
                raise FrameTooLargeByteStreamBufferError('frame exceeded max_frame_length')

            # If we don't have the full frame yet, either wait or (optionally) fail fast if buffering is clearly out of
            # control.
            if len(buf) < total_len:
                if self._max is not None and len(buf) > self._max:
                    raise BufferTooLargeByteStreamBufferError(
                        'buffer exceeded max_frame_length without completing a frame',
                    )
                return out

            # We have a complete frame available.
            if self._strip:
                if self._strip > total_len:
                    raise ValueError('initial_bytes_to_strip > frame length')
                buf.advance(self._strip)
                total_len -= self._strip

            out.append(buf.split_to(total_len))

            # Loop for additional frames
