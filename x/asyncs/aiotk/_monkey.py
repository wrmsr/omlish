# -*- coding: utf-8 -*-


import asyncio


def monkey_patch() -> None:
    """Applies all monkey patches.

    This is a series of backports for asyncio functions in order to use them on
    all Python 3.5+ versions.

    .. versionadded:: 0.1

    """

    if not hasattr(asyncio.StreamReader, 'readuntil'):  # pragma: no cover
        asyncio.StreamReader.readuntil = readuntil  # type: ignore


# Appears in Python 3.5.2.
async def readuntil(self, separator=b'\n'):  # pragma: no cover
    """Read data from the stream until ``separator`` is found.

    On success, the data and separator will be removed from the
    internal buffer (consumed). Returned data will include the
    separator at the end.

    Configured stream limit is used to check result. Limit sets the
    maximal length of data that can be returned, not counting the
    separator.

    If an EOF occurs and the complete separator is still not found,
    an IncompleteReadError exception will be raised, and the internal
    buffer will be reset.  The IncompleteReadError.partial attribute
    may contain the separator partially.

    If the data cannot be read because of over limit, a
    LimitOverrunError exception  will be raised, and the data
    will be left in the internal buffer, so it can be read again.

    .. versionadded:: 0.1

    """
    seplen = len(separator)
    if seplen == 0:
        raise ValueError('Separator should be at least one-byte string')
    if self._exception is not None:
        raise self._exception

    # Consume whole buffer except last bytes, which length is
    # one less than seplen. Let's check corner cases with
    # separator='SEPARATOR':
    # * we have received almost complete separator (without last
    #   byte). i.e buffer='some textSEPARATO'. In this case we
    #   can safely consume len(separator) - 1 bytes.
    # * last byte of buffer is first byte of separator, i.e.
    #   buffer='abcdefghijklmnopqrS'. We may safely consume
    #   everything except that last byte, but this require to
    #   analyze bytes of buffer that match partial separator.
    #   This is slow and/or require FSM. For this case our
    #   implementation is not optimal, since require rescanning
    #   of data that is known to not belong to separator. In
    #   real world, separator will not be so long to notice
    #   performance problems. Even when reading MIME-encoded
    #   messages :)

    # `offset` is the number of bytes from the beginning of the buffer
    # where there is no occurrence of `separator`.
    offset = 0

    # Loop until we find `separator` in the buffer, exceed the buffer size,
    # or an EOF has happened.
    while True:
        buflen = len(self._buffer)

        # Check if we now have enough data in the buffer for `separator` to
        # fit.
        if buflen - offset >= seplen:
            isep = self._buffer.find(separator, offset)

            if isep != -1:
                # `separator` is in the buffer. `isep` will be used later
                # to retrieve the data.
                break

            # see upper comment for explanation.
            offset = buflen + 1 - seplen
            if offset > self._limit:
                raise asyncio.LimitOverrunError(
                    'Separator is not found, and chunk exceed the limit',
                    offset)

        # Complete message (with full separator) may be present in buffer
        # even when EOF flag is set. This may happen when the last chunk
        # adds data which makes separator be found. That's why we check for
        # EOF *ater* inspecting the buffer.
        if self._eof:
            chunk = bytes(self._buffer)
            self._buffer.clear()
            raise asyncio.IncompleteReadError(chunk, None)

        # _wait_for_data() will resume reading if stream was paused.
        await self._wait_for_data('readuntil')

    if isep > self._limit:
        raise asyncio.LimitOverrunError(
            'Separator is found, but chunk is longer than limit', isep)

    chunk = self._buffer[:isep + seplen]
    del self._buffer[:isep + seplen]
    self._maybe_resume_transport()
    return bytes(chunk)
