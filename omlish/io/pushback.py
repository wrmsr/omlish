# @omlish-lite
import typing as ta


##


class PushbackReader:
    """
    Wrap a non-seekable stream (e.g. socket.makefile('rb') or BufferedReader)
    and provide:
      - read(n=-1)
      - readline(limit=-1)
      - readuntil(delim, max_bytes, include_delim=True, chunk_size=8192)

    Extra bytes read past a delimiter are kept in an internal pushback buffer and returned on subsequent reads/readline
    calls.
    """

    def __init__(self, raw):
        self._raw = raw
        self._pushback = bytearray()

    class MaxLengthExceededError(Exception):
        pass

    def read(self, n: int = -1) -> bytes:
        if n == 0:
            return b''

        # read all
        if n < 0:
            out = bytes(self._pushback)
            self._pushback.clear()
            rest = self._raw.read(-1)
            return out + (rest or b'')

        # satisfy from pushback first
        if len(self._pushback) >= n:
            out = bytes(self._pushback[:n])
            del self._pushback[:n]
            return out

        out = bytes(self._pushback)
        self._pushback.clear()
        need = n - len(out)
        chunk = self._raw.read(need) or b''
        return out + chunk

    def readline(self, limit: int = -1) -> bytes:
        # If limit is set, we must not exceed it.
        if limit == 0:
            return b''

        # First, see if pushback already contains a full line.
        nl = self._pushback.find(b'\n')
        if nl != -1:
            end = nl + 1
            if limit > -1:
                end = min(end, limit)
            out = bytes(self._pushback[:end])
            del self._pushback[:end]
            return out

        # Otherwise, accumulate until newline or limit or EOF.
        buf = bytearray()
        if self._pushback:
            buf += self._pushback
            self._pushback.clear()

        while True:
            # Stop if limit reached
            if limit > -1 and len(buf) >= limit:
                return bytes(buf[:limit])

            # Read more
            # Choose a chunk size that respects limit
            to_read = 8192
            if limit > -1:
                to_read = min(to_read, limit - len(buf))
            chunk = self._raw.read1(to_read)
            if not chunk:
                return bytes(buf)

            buf += chunk
            nl = buf.find(b'\n')
            if nl != -1:
                end = nl + 1
                if limit > -1:
                    end = min(end, limit)
                out = bytes(buf[:end])
                # push back anything after the returned part
                if end < len(buf):
                    self._pushback += buf[end:]
                return out

    def readuntil(
            self,
            delim: bytes,
            *,
            max_bytes: ta.Optional[int] = None,
            include_delim: bool = True,
            chunk_size: int = 8192,
    ) -> bytes:
        if not delim:
            raise ValueError('delim must be non-empty')
        if max_bytes is not None and max_bytes < 0:
            raise ValueError('max_bytes must be >= 0')

        buf = bytearray()

        # start with any pushback data
        if self._pushback:
            buf += self._pushback
            self._pushback.clear()

        while True:
            idx = buf.find(delim)
            if idx != -1:
                end = idx + (len(delim) if include_delim else 0)
                out = bytes(buf[:end])
                # push back everything after the delimiter (or after idx+len(delim))
                tail_start = idx + len(delim)
                if tail_start < len(buf):
                    self._pushback += buf[tail_start:]
                return out

            if max_bytes is not None:
                if len(buf) >= max_bytes:
                    raise PushbackReader.MaxLengthExceededError(f'Delimiter not found within {max_bytes} bytes')
                # read another chunk, but don't exceed max_bytes by too much
                to_read = min(chunk_size, max_bytes - len(buf))
            else:
                to_read = chunk_size

            chunk = self._raw.read1(to_read)
            if not chunk:
                raise EOFError('EOF reached before delimiter was found')
            buf += chunk
