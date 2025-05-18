import collections.abc
import email.parser
import enum
import http
import io
import typing as ta
import urllib.parse

from omlish.lite.check import check
from omlish.lite.maybes import Maybe

from .errors import BadStatusLineError
from .errors import CannotSendHeaderError
from .errors import CannotSendRequestError
from .errors import ClientError
from .errors import IncompleteReadError
from .errors import InvalidUrlError
from .errors import LineTooLongError
from .errors import NotConnectedError
from .errors import RemoteDisconnectedError
from .errors import ResponseNotReadyError
from .errors import UnknownProtocolError
from .io import CloseIo
from .io import ConnectIo
from .io import Io
from .io import ReadIo
from .io import ReadLineIo
from .io import WriteIo
from .validation import HttpClientValidation


##


_MAX_LINE = 65536


class RawHttpConnection:
    def _close_conn(self) -> None:
        self._closed = True

    def close(self) -> None:
        if not self._closed:
            self._close_conn()

    def _read_next_chunk_size(self) -> ta.Generator[Io, ta.Optional[bytes], int]:
        # Read the next chunk size from the file
        line = check.isinstance((yield ReadLineIo(_MAX_LINE + 1)), bytes)
        if len(line) > _MAX_LINE:
            raise LineTooLongError('chunk size')

        i = line.find(b';')
        if i >= 0:
            line = line[:i] # strip chunk-extensions

        try:
            return int(line, 16)
        except ValueError:
            # close the connection as protocol synchronisation is probably lost
            self._close_conn()
            raise

    def _read_and_discard_trailer(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        # Read and discard trailer up to the CRLF terminator
        # NOTE: we shouldn't have any trailers!
        while True:
            line = check.isinstance((yield ReadLineIo(_MAX_LINE + 1)), bytes)
            if len(line) > _MAX_LINE:
                raise LineTooLongError('trailer line')

            if not line:
                # a vanishingly small number of sites EOF without sending the trailer
                break

            if line in (b'\r\n', b'\n', b''):
                break

    def _get_chunk_left(self) -> ta.Generator[Io, ta.Optional[bytes], ta.Any]:
        # Return self.chunk_left, reading a new chunk if necessary. chunk_left == 0: at the end of the current chunk,
        # need to close it chunk_left == None: No current chunk, should read next. This function returns non-zero or
        # None if the last chunk has been read.
        chunk_left = self.chunk_left
        if not chunk_left: # Can be 0 or None
            if chunk_left is not None:
                # We are at the end of chunk, discard chunk end
                yield from self._safe_read(2)  # toss the CRLF at the end of the chunk

            try:
                chunk_left = yield from self._read_next_chunk_size()
            except ValueError:
                raise IncompleteReadError(b'') from None

            if chunk_left == 0:
                # last chunk: 1*('0') [ chunk-extension ] CRLF
                yield from self._read_and_discard_trailer()

                # we read everything; close the 'file'
                self._close_conn()

                chunk_left = None

            self.chunk_left = chunk_left

        return chunk_left

    def _read_chunked(self, amt: ta.Optional[int] = None) -> ta.Generator[Io, ta.Optional[bytes], bytes]:
        value = []
        try:
            while (chunk_left := (yield from self._get_chunk_left())) is not None:
                if amt is not None and amt <= chunk_left:
                    value.append((yield from self._safe_read(amt)))
                    self.chunk_left = chunk_left - amt
                    break

                value.append((yield from self._safe_read(chunk_left)))
                if amt is not None:
                    amt -= chunk_left
                self.chunk_left = 0

            return b''.join(value)

        except IncompleteReadError as exc:
            raise IncompleteReadError(b''.join(value)) from exc

    def _safe_read(self, amt: int) -> ta.Generator[Io, ta.Optional[bytes], bytes]:
        """
        Read the number of bytes requested.

        This function should be used when <amt> bytes "should" be present for reading. If the bytes are truly not
        available (due to EOF), then the IncompleteRead exception can be used to detect the problem.
        """

        data = check.isinstance((yield ReadIo(amt)), bytes)
        if len(data) < amt:
            raise IncompleteReadError(data, amt-len(data))
        return data

    def peek(self, n: int = -1) -> ta.Generator[Io, ta.Optional[bytes], bytes]:
        # Having this enables IOBase.readline() to read more than one byte at a time
        if self._closed:
            return b''

        if self.chunked:
            return self._peek_chunked(n)

        return self.fp.peek(n)

    def _readline(self, size=-1):
        # For backwards compatibility, a (slowish) readline().
        if hasattr(self, 'peek'):
            def nreadahead():
                readahead = self.peek(1)
                if not readahead:
                    return 1
                n = (readahead.find(b'\n') + 1) or len(readahead)
                if size >= 0:
                    n = min(n, size)
                return n

        else:
            def nreadahead():
                return 1

        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f'{size!r} is not an integer') from None
            else:
                size = size_index()

        res = bytearray()
        while size < 0 or len(res) < size:
            b = self.read(nreadahead())
            if not b:
                break
            res += b
            if res.endswith(b'\n'):
                break

        return bytes(res)

    def readline(self, limit: int = -1) -> bytes:
        if self.chunked:
            # Fallback to IOBase readline which uses peek() and read()
            return self._readline(limit)

        if self.length is not None and (limit < 0 or limit > self.length):
            limit = self.length

        result = self.fp.readline(limit)

        if not result and limit:
            self._close_conn()

        elif self.length is not None:
            self.length -= len(result)
            if not self.length:
                self._close_conn()

        return result

    def _peek_chunked(self, n: int) -> bytes:
        # Strictly speaking, _get_chunk_left() may cause more than one read, but that is ok, since that is to satisfy
        # the chunked protocol.
        try:
            chunk_left = self._get_chunk_left()
        except IncompleteReadError:
            return b'' # peek doesn't worry about protocol

        if chunk_left is None:
            return b'' # eof

        # peek is allowed to return more than requested. Just request the entire chunk, and truncate what we get.
        return self.fp.peek(chunk_left)[:chunk_left]

    def send(self, data: ta.Any) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """
        Send `data' to the server. ``data`` can be a string object, a bytes object, an array object, a file-like object
        that supports a .read() method, or an iterable object.
        """

        if hasattr(data, 'read'):
            encode = self._is_text_io(data)
            while data_block := data.read(self._block_size):
                if encode:
                    data_block = data_block.encode('iso-8859-1')
                check.none((yield WriteIo(data_block)))
            return

        if isinstance(data, (bytes, bytearray)):
            check.none((yield WriteIo(data)))

        elif isinstance(data, collections.abc.Iterable):
            for d in data:
                check.none((yield WriteIo(d)))

        else:
            raise TypeError(f'data should be a bytes-like object or an iterable, got {type(data)!r}') from None

    def _output(self, s: bytes) -> None:
        """
        Add a line of output to the current request buffer.

        Assumes that the line does *not* end with \\r\\n.
        """

        self._buffer.append(s)

    def _read_readable(self, readable: ta.Union[ta.IO, ta.TextIO]) -> ta.Iterator[bytes]:
        while data := readable.read(self._block_size):
            if isinstance(data, str):
                yield data.encode('iso-8859-1')
            else:
                yield data

    def _send_output(
            self,
            message_body: ta.Optional[ta.Any] = None,
            encode_chunked: bool = False,
    ) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """
        Send the currently buffered request and clear the buffer.

        Appends an extra \\r\\n to the buffer. A message_body may be specified, to be appended to the request.
        """

        self._buffer.extend((b'', b''))
        msg = b'\r\n'.join(self._buffer)
        del self._buffer[:]
        yield from self.send(msg)

        chunks: ta.Iterable[bytes]
        if message_body is not None:
            # create a consistent interface to message_body
            if hasattr(message_body, 'read'):
                # Let file-like take precedence over byte-like. This is needed to allow the current position of mmap'ed
                # files to be taken into account.
                chunks = self._read_readable(message_body)

            else:
                try:
                    # this is solely to check to see if message_body implements the buffer API. it /would/ be easier to
                    # capture if PyObject_CheckBuffer was exposed to Python.
                    memoryview(message_body)

                except TypeError:
                    try:
                        chunks = iter(message_body)
                    except TypeError as e:
                        raise TypeError(
                            f'message_body should be a bytes-like object or an iterable, got {type(message_body)!r}',
                        ) from e

                else:
                    # the object implements the buffer interface and can be passed directly into socket methods
                    chunks = (message_body,)

            for chunk in chunks:
                if not chunk:
                    continue

                if encode_chunked and self._http_version == 11:
                    # chunked encoding
                    chunk = f'{len(chunk):X}\r\n'.encode('ascii') + chunk + b'\r\n'
                yield from self.send(chunk)

            if encode_chunked and self._http_version == 11:
                # end chunked transfer
                yield from self.send(b'0\r\n\r\n')
