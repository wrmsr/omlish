# @omlish-lite
# ruff: noqa: UP006 UP007 UP043 UP045
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import email.parser
import http
import typing as ta

from ....lite.check import check
from ..io import CoroHttpIo
from .errors import CoroHttpClientErrors
from .headers import CoroHttpClientHeaders
from .status import CoroHttpClientStatusLine


##


class CoroHttpClientResponse:
    # See RFC 2616 sec 19.6 and RFC 1945 sec 6 for details.

    # The bytes from the socket object are iso-8859-1 strings. See RFC 2616 sec 2.2 which notes an exception for
    # MIME-encoded text following RFC 2047. The basic status line parsing only accepts iso-8859-1.

    def __init__(self, method: str) -> None:
        super().__init__()

        state = self._State()
        state.method = method
        self._state = state

    class _State:
        closed: bool = False

        # If the response includes a content-length header, we need to make sure that the client doesn't read more than
        # the specified number of bytes. If it does, it will block until the server times out and closes the connection.
        # This will happen if a read is done (without a size) whether self.fp is buffered or not. So, no read by clients
        # unless they know what they are doing.
        method: str

        # The HttpResponse object is returned via urllib. The clients of http and urllib expect different attributes for
        # the headers. headers is used here and supports urllib. msg is provided as a backwards compatibility layer for
        # http clients.
        headers: email.message.Message

        # From the Status-Line of the response
        version: int  # HTTP-Version
        status: int  # Status-Code
        reason: str  # Reason-Phrase

        chunked: bool  # Is "chunked" being used?
        chunk_left: ta.Optional[int]  # Bytes left to read in current chunk
        length: ta.Optional[int]  # Number of bytes left in response
        will_close: bool  # Conn will close at end of response

    #

    def _read_status(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], CoroHttpClientStatusLine]:
        try:
            return (yield from CoroHttpClientStatusLine.read())
        except CoroHttpClientErrors.BadStatusLineError:
            self._close_conn()
            raise

    def _begin(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], None]:
        state = self._state

        check.state(not hasattr(state, 'headers'))

        # Read until we get a non-100 response
        while True:
            version, status, reason = yield from self._read_status()
            if status != http.HTTPStatus.CONTINUE:
                break

            # Skip the header from the 100 response
            skipped_headers = yield from CoroHttpClientHeaders.read_headers()  # noqa

            del skipped_headers

        state.status = status
        state.reason = reason.strip()
        if version in ('HTTP/1.0', 'HTTP/0.9'):
            # Some servers might still return '0.9', treat it as 1.0 anyway
            state.version = 10
        elif version.startswith('HTTP/1.'):
            # Use HTTP/1.1 code for HTTP/1.x where x>=1
            state.version = 11
        else:
            raise CoroHttpClientErrors.UnknownProtocolError(version)

        state.headers = yield from CoroHttpClientHeaders.parse_headers()

        # Are we using the chunked-style of transfer encoding?
        tr_enc = state.headers.get('transfer-encoding')
        if tr_enc and tr_enc.lower() == 'chunked':
            state.chunked = True
            state.chunk_left = None
        else:
            state.chunked = False

        # Will the connection close at the end of the response?
        state.will_close = self._check_close()

        # Do we have a Content-Length?
        # NOTE: RFC 2616, S4.4, #3 says we ignore this if tr_enc is 'chunked'
        state.length = None
        length = state.headers.get('content-length')
        if length and not state.chunked:
            try:
                state.length = int(length)
            except ValueError:
                state.length = None
            else:
                if state.length < 0:  # Ignore nonsensical negative lengths
                    state.length = None
        else:
            state.length = None

        # Does the body have a fixed length? (of zero)
        if (
                status in (http.HTTPStatus.NO_CONTENT, http.HTTPStatus.NOT_MODIFIED) or
                100 <= status < 200 or  # 1xx codes
                state.method == 'HEAD'
        ):
            state.length = 0

        # If the connection remains open, and we aren't using chunked, and a content-length was not provided, then
        # assume that the connection WILL close.
        if (
                not state.will_close and
                not state.chunked and
                state.length is None
        ):
            state.will_close = True

    #

    def _check_close(self) -> bool:
        conn = self._state.headers.get('connection')
        if getattr(self._state, 'version', None) == 11:
            # An HTTP/1.1 proxy is assumed to stay open unless explicitly closed.
            if conn and 'close' in conn.lower():
                return True
            return False

        # Some HTTP/1.0 implementations have support for persistent connections, using rules different than HTTP/1.1.

        # For older HTTP, Keep-Alive indicates persistent connection.
        if self._state.headers.get('keep-alive'):
            return False

        # At least Akamai returns a 'Connection: Keep-Alive' header, which was supposed to be sent by the client.
        if conn and 'keep-alive' in conn.lower():
            return False

        # Proxy-Connection is a netscape hack.
        pconn = self._state.headers.get('proxy-connection')
        if pconn and 'keep-alive' in pconn.lower():
            return False

        # Otherwise, assume it will close
        return True

    def _close_conn(self) -> None:
        self._state.closed = True

    def close(self) -> None:
        if not self._state.closed:
            self._close_conn()

    def is_closed(self) -> bool:
        """True if the connection is closed."""

        # NOTE: it is possible that we will not ever call self.close(). This case occurs when will_close is TRUE, length
        #   is None, and we read up to the last byte, but NOT past it.
        #
        # IMPLIES: if will_close is FALSE, then self.close() will ALWAYS be called, meaning self.is_closed() is
        #   meaningful.
        return self._state.closed

    #

    def read(self, amt: ta.Optional[int] = None) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        """Read and return the response body, or up to the next amt bytes."""

        if self._state.closed:
            return b''

        if self._state.method == 'HEAD':
            self._close_conn()
            return b''

        if self._state.chunked:
            return (yield from self._read_chunked(amt))

        if amt is not None and amt >= 0:
            if self._state.length is not None and amt > self._state.length:
                # Clip the read to the "end of response"
                amt = self._state.length

            s = check.isinstance((yield CoroHttpIo.ReadIo(amt)), bytes)

            if not s and amt:
                # Ideally, we would raise IncompleteRead if the content-length wasn't satisfied, but it might break
                # compatibility.
                self._close_conn()

            elif self._state.length is not None:
                self._state.length -= len(s)
                if not self._state.length:
                    self._close_conn()

            return s

        else:
            # Amount is not given (unbounded read) so we must check self.length
            if self._state.length is None:
                s = check.isinstance((yield CoroHttpIo.ReadIo(None)), bytes)

            else:
                try:
                    s = yield from self._safe_read(self._state.length)
                except CoroHttpClientErrors.IncompleteReadError:
                    self._close_conn()
                    raise

                self._state.length = 0

            self._close_conn()  # We read everything
            return s

    def _read_next_chunk_size(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], int]:
        # Read the next chunk size from the file
        line = check.isinstance((yield CoroHttpIo.ReadLineIo(CoroHttpIo.MAX_LINE + 1)), bytes)
        if len(line) > CoroHttpIo.MAX_LINE:
            raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.CHUNK_SIZE)

        i = line.find(b';')
        if i >= 0:
            line = line[:i]  # Strip chunk-extensions

        try:
            return int(line, 16)
        except ValueError:
            # Close the connection as protocol synchronisation is probably lost
            self._close_conn()
            raise

    def _read_and_discard_trailer(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], None]:
        # Read and discard trailer up to the CRLF terminator
        # NOTE: we shouldn't have any trailers!
        while True:
            line = check.isinstance((yield CoroHttpIo.ReadLineIo(CoroHttpIo.MAX_LINE + 1)), bytes)
            if len(line) > CoroHttpIo.MAX_LINE:
                raise CoroHttpClientErrors.LineTooLongError(CoroHttpClientErrors.LineTooLongError.LineType.TRAILER)

            if not line:
                # A vanishingly small number of sites EOF without sending the trailer
                break

            if line in (b'\r\n', b'\n', b''):
                break

    def _get_chunk_left(self) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], ta.Optional[int]]:
        # Return self.chunk_left, reading a new chunk if necessary. chunk_left == 0: at the end of the current chunk,
        # need to close it chunk_left == None: No current chunk, should read next. This function returns non-zero or
        # None if the last chunk has been read.
        chunk_left = self._state.chunk_left
        if not chunk_left:  # Can be 0 or None
            if chunk_left is not None:
                # We are at the end of chunk, discard chunk end
                yield from self._safe_read(2)  # Toss the CRLF at the end of the chunk

            try:
                chunk_left = yield from self._read_next_chunk_size()
            except ValueError:
                raise CoroHttpClientErrors.IncompleteReadError(b'') from None

            if chunk_left == 0:
                # Last chunk: 1*('0') [ chunk-extension ] CRLF
                yield from self._read_and_discard_trailer()

                # We read everything; close the 'file'
                self._close_conn()

                chunk_left = None

            self._state.chunk_left = chunk_left

        return chunk_left

    def _read_chunked(
            self,
            amt: ta.Optional[int] = None,
    ) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        check.state(hasattr(self._state, 'chunked'))
        if amt is not None and amt < 0:
            amt = None
        value = []
        try:
            while (chunk_left := (yield from self._get_chunk_left())) is not None:
                if amt is not None and amt <= chunk_left:
                    value.append((yield from self._safe_read(amt)))
                    self._state.chunk_left = chunk_left - amt
                    break

                value.append((yield from self._safe_read(chunk_left)))
                if amt is not None:
                    amt -= chunk_left
                self._state.chunk_left = 0

            return b''.join(value)

        except CoroHttpClientErrors.IncompleteReadError as exc:
            raise CoroHttpClientErrors.IncompleteReadError(b''.join(value)) from exc

    def _safe_read(self, amt: int) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        """
        Read the number of bytes requested.

        This function should be used when <amt> bytes "should" be present for reading. If the bytes are truly not
        available (due to EOF), then the IncompleteRead exception can be used to detect the problem.
        """

        data = check.isinstance((yield CoroHttpIo.ReadIo(amt)), bytes)
        if len(data) < amt:
            raise CoroHttpClientErrors.IncompleteReadError(data, amt - len(data))
        return data

    def peek(self, n: int = -1) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        # Having this enables IOBase.readline() to read more than one byte at a time
        if self._state.closed or self._state.method == 'HEAD':
            return b''

        if self._state.chunked:
            return (yield from self._peek_chunked(n))

        return check.isinstance((yield CoroHttpIo.PeekIo(n)), bytes)

    def _readline(
            self,
            size: ta.Optional[int] = -1,
    ) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f'{size!r} is not an integer') from None
            else:
                size = size_index()

        # For backwards compatibility, a (slowish) readline().
        def nreadahead():
            readahead = yield from self.peek(1)
            if not readahead:
                return 1
            n = (readahead.find(b'\n') + 1) or len(readahead)
            if size >= 0:
                n = min(n, size)
            return n

        res = bytearray()
        while size < 0 or len(res) < size:
            b = (yield from self.read((yield from nreadahead())))
            if not b:
                break
            res += b
            if res.endswith(b'\n'):
                break

        return bytes(res)

    def readline(self, limit: int = -1) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        if self._state.closed or self._state.method == 'HEAD':
            return b''

        if self._state.chunked:
            # Fallback to IOBase readline which uses peek() and read()
            return (yield from self._readline(limit))

        if self._state.length is not None and (limit < 0 or limit > self._state.length):
            limit = self._state.length

        result = check.isinstance((yield CoroHttpIo.ReadLineIo(limit)), bytes)

        if not result and limit:
            self._close_conn()

        elif self._state.length is not None:
            self._state.length -= len(result)
            if not self._state.length:
                self._close_conn()

        return result

    def _peek_chunked(self, n: int) -> ta.Generator[CoroHttpIo.Io, ta.Optional[bytes], bytes]:
        # Strictly speaking, _get_chunk_left() may cause more than one read, but that is ok, since that is to satisfy
        # the chunked protocol.
        try:
            chunk_left = yield from self._get_chunk_left()
        except CoroHttpClientErrors.IncompleteReadError:
            return b''  # Peek doesn't worry about protocol

        if chunk_left is None:
            return b''  # Eof

        # Peek is allowed to return more than requested. Just request the entire chunk, and truncate what we get.
        return check.isinstance((yield CoroHttpIo.PeekIo(chunk_left)), bytes)[:chunk_left]
