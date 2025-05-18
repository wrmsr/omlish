# ruff: noqa: I001 UP006 UP007
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
# 4. PSF is making Python available to Licensee on an "AS IS" basis. PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS
# OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF
# MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee. This License Agreement does not grant permission to use PSF trademarks or trade name
# in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
"""
https://github.com/python/cpython/blob/9b335cc8104dd83a5a1343dc649d1f3606682098/Lib/http/client.py
"""
import abc
import collections.abc
import dataclasses as dc
import email.parser
import enum
import errno
import http
import io
import socket
import typing as ta
import urllib.parse

from omlish.lite.check import check

from .validation import HttpClientValidation


##


class ClientError(Exception):
    pass


class NotConnectedError(ClientError):
    pass


class InvalidUrlError(ClientError):
    pass


@dc.dataclass()
class UnknownProtocolError(ClientError):
    version: str


@dc.dataclass()
class IncompleteReadError(ClientError):
    partial: bytes
    expected: ta.Optional[int] = None


class ImproperConnectionStateError(ClientError):
    pass


class CannotSendRequestError(ImproperConnectionStateError):
    pass


class CannotSendHeaderError(ImproperConnectionStateError):
    pass


class ResponseNotReadyError(ImproperConnectionStateError):
    pass


@dc.dataclass()
class BadStatusLineError(ClientError):
    line: str


class RemoteDisconnectedError(BadStatusLineError, ConnectionResetError):
    pass


@dc.dataclass()
class LineTooLongError(ClientError):
    line_type: str


##


class Io(abc.ABC):  # noqa
    pass


#


@dc.dataclass(frozen=True)
class ConnectIo(Io):
    args: ta.Tuple[ta.Any, ...]
    kwargs: ta.Optional[ta.Dict[str, ta.Any]] = None


class CloseIo(Io):
    pass


#

class AnyReadIo(Io):  # noqa
    pass


@dc.dataclass(frozen=True)
class ReadIo(AnyReadIo):
    sz: ta.Optional[int]


@dc.dataclass(frozen=True)
class ReadLineIo(AnyReadIo):
    sz: int


#

@dc.dataclass(frozen=True)
class WriteIo(Io):
    data: bytes


##


HTTP_PORT = 80
HTTPS_PORT = 443

_UNKNOWN = 'UNKNOWN'

_METHODS_EXPECTING_BODY = {'PATCH', 'POST', 'PUT'}

_MAX_LINE = 65536
_MAX_HEADERS = 100


def _read_headers() -> ta.Generator[Io, ta.Optional[bytes], ta.List[bytes]]:
    """
    Reads potential header lines into a list from a file pointer.

    Length of line is limited by _MAX_LINE, and number of headers is limited by _MAX_HEADERS.
    """

    headers = []
    while True:
        line = check.isinstance((yield ReadLineIo(_MAX_LINE + 1)), bytes)
        if len(line) > _MAX_LINE:
            raise LineTooLongError('header line')

        headers.append(line)
        if len(headers) > _MAX_HEADERS:
            raise ClientError(f'got more than {_MAX_HEADERS} headers')

        if line in (b'\r\n', b'\n', b''):
            break

    return headers


def _parse_header_lines(header_lines: ta.Sequence[bytes]) -> email.message.Message:
    """
    Parses only RFC2822 headers from header lines.

    email Parser wants to see strings rather than bytes. But a TextIOWrapper around self.rfile would buffer too many
    bytes from the stream, bytes which we later need to read as bytes. So we read the correct bytes here, as bytes, for
    email Parser to parse.
    """

    text = b''.join(header_lines).decode('iso-8859-1')
    return email.parser.Parser().parsestr(text)


def parse_headers() -> ta.Generator[Io, ta.Optional[bytes], email.message.Message]:
    """Parses only RFC2822 headers from a file pointer."""

    headers = yield from _read_headers()
    return _parse_header_lines(headers)


def _encode(data: str, name: str = 'data') -> bytes:
    """Call data.encode("latin-1") but show a better error message."""

    try:
        return data.encode('latin-1')

    except UnicodeEncodeError as err:
        raise UnicodeEncodeError(
            err.encoding,
            err.object,
            err.start,
            err.end,
            "%s (%.20r) is not valid Latin-1. Use %s.encode('utf-8') if you want to send it encoded in UTF-8." % (  # noqa
                name.title(),
                data[err.start:err.end],
                name,
            ),
        ) from None


def _strip_ipv6_iface(enc_name: bytes) -> bytes:
    """Remove interface scope from IPv6 address."""

    enc_name, percent, _ = enc_name.partition(b'%')
    if percent:
        check.state(enc_name.startswith(b'['))
        enc_name += b']'
    return enc_name


class HttpResponse:
    # See RFC 2616 sec 19.6 and RFC 1945 sec 6 for details.

    # The bytes from the socket object are iso-8859-1 strings. See RFC 2616 sec 2.2 which notes an exception for
    # MIME-encoded text following RFC 2047. The basic status line parsing only accepts iso-8859-1.

    def __init__(
            self,
            method: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._closed = False

        # If the response includes a content-length header, we need to make sure that the client doesn't read more than
        # the specified number of bytes. If it does, it will block until the server times out and closes the connection.
        # This will happen if a self.fp.read() is done (without a size) whether self.fp is buffered or not. So, no
        # self.fp.read() by clients unless they know what they are doing.
        self._method = method

        # The HttpResponse object is returned via urllib. The clients of http and urllib expect different attributes for
        # the headers. headers is used here and supports urllib. msg is provided as a backwards compatibility layer for
        # http clients.
        self.headers: ta.Optional[email.message.Message] = None

        # from the Status-Line of the response
        self.version = _UNKNOWN  # HTTP-Version
        self.status = _UNKNOWN   # Status-Code
        self.reason = _UNKNOWN   # Reason-Phrase

        self.chunked = _UNKNOWN     # is "chunked" being used?
        self.chunk_left = _UNKNOWN  # bytes left to read in current chunk
        self.length = _UNKNOWN      # number of bytes left in response
        self.will_close = _UNKNOWN  # conn will close at end of response

    class _StatusLine(ta.NamedTuple):
        version: str
        status: int
        reason: str

    def _read_status(self) -> ta.Generator[Io, ta.Optional[bytes], _StatusLine]:
        line = str(check.isinstance((yield ReadLineIo(_MAX_LINE + 1)), bytes), 'iso-8859-1')
        if len(line) > _MAX_LINE:
            raise LineTooLongError('status line')
        if not line:
            # Presumably, the server closed the connection before sending a valid response.
            raise RemoteDisconnectedError('Remote end closed connection without response')

        version = ''
        reason = ''
        status_str = ''
        try:
            version, status_str, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status_str = line.split(None, 1)
            except ValueError:
                # empty version will cause next test to fail.
                pass

        if not version.startswith('HTTP/'):
            self._close_conn()
            raise BadStatusLineError(line)

        # The status code is a three-digit number
        try:
            status = int(status_str)
        except ValueError:
            raise BadStatusLineError(line) from None

        if status < 100 or status > 999:
            raise BadStatusLineError(line)

        return self._StatusLine(version, status, reason)

    def begin(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        if self.headers is not None:
            # we've already started reading the response
            return

        # read until we get a non-100 response
        while True:
            version, status, reason = yield from self._read_status()
            if status != http.HTTPStatus.CONTINUE:
                break

            # skip the header from the 100 response
            skipped_headers = yield from _read_headers()

            del skipped_headers

        self.code = self.status = status
        self.reason = reason.strip()
        if version in ('HTTP/1.0', 'HTTP/0.9'):
            # Some servers might still return '0.9', treat it as 1.0 anyway
            self.version = 10
        elif version.startswith('HTTP/1.'):
            self.version = 11   # use HTTP/1.1 code for HTTP/1.x where x>=1
        else:
            raise UnknownProtocolError(version)

        self.headers = yield from parse_headers()

        # are we using the chunked-style of transfer encoding?
        tr_enc = self.headers.get('transfer-encoding')
        if tr_enc and tr_enc.lower() == 'chunked':
            self.chunked = True
            self.chunk_left = None
        else:
            self.chunked = False

        # will the connection close at the end of the response?
        self.will_close = self._check_close()

        # do we have a Content-Length?
        # NOTE: RFC 2616, S4.4, #3 says we ignore this if tr_enc is 'chunked'
        self.length = None
        length = self.headers.get('content-length')
        if length and not self.chunked:
            try:
                self.length = int(length)
            except ValueError:
                self.length = None
            else:
                if self.length < 0:  # ignore nonsensical negative lengths
                    self.length = None
        else:
            self.length = None

        # does the body have a fixed length? (of zero)
        if (
                status in (http.HTTPStatus.NO_CONTENT, http.HTTPStatus.NOT_MODIFIED) or
                100 <= status < 200 or # 1xx codes
                self._method == 'HEAD'
        ):
            self.length = 0

        # if the connection remains open, and we aren't using chunked, and a content-length was not provided, then
        # assume that the connection WILL close.
        if not self.will_close and not self.chunked and self.length is None:
            self.will_close = True

    def _check_close(self) -> bool:
        conn = self.headers.get('connection')
        if self.version == 11:
            # An HTTP/1.1 proxy is assumed to stay open unless explicitly closed.
            if conn and 'close' in conn.lower():
                return True
            return False

        # Some HTTP/1.0 implementations have support for persistent connections, using rules different than HTTP/1.1.

        # For older HTTP, Keep-Alive indicates persistent connection.
        if self.headers.get('keep-alive'):
            return False

        # At least Akamai returns a 'Connection: Keep-Alive' header,
        # which was supposed to be sent by the client.
        if conn and 'keep-alive' in conn.lower():
            return False

        # Proxy-Connection is a netscape hack.
        pconn = self.headers.get('proxy-connection')
        if pconn and 'keep-alive' in pconn.lower():
            return False

        # otherwise, assume it will close
        return True

    def _close_conn(self) -> None:
        self._closed = True

    def close(self) -> None:
        if not self._closed:
            self._close_conn()

    # These implementations are for the benefit of io.BufferedReader.

    # XXX This class should probably be revised to act more like the 'raw stream' that BufferedReader expects.

    def readable(self) -> bool:
        """Always returns True"""

        return True

    # End of "raw stream" methods

    def isclosed(self) -> bool:
        """True if the connection is closed."""

        # NOTE: it is possible that we will not ever call self.close(). This case occurs when will_close is TRUE, length
        #   is None, and we read up to the last byte, but NOT past it.
        #
        # IMPLIES: if will_close is FALSE, then self.close() will ALWAYS be called, meaning self.isclosed() is
        #   meaningful.
        return self._closed

    def read(self, amt: ta.Optional[int] = None) -> ta.Generator[Io, ta.Optional[bytes], bytes]:
        """Read and return the response body, or up to the next amt bytes."""

        if self._closed is None:
            return b''

        if self._method == 'HEAD':
            self._close_conn()
            return b''

        if self.chunked:
            return (yield from self._read_chunked(amt))

        if amt is not None:
            if self.length is not None and amt > self.length:
                # clip the read to the "end of response"
                amt = self.length

            s = check.isinstance((yield ReadIo(amt)), bytes)

            if not s and amt:
                # Ideally, we would raise IncompleteRead if the content-length wasn't satisfied, but it might break
                # compatibility.
                self._close_conn()

            elif self.length is not None:
                self.length -= len(s)
                if not self.length:
                    self._close_conn()

            return s

        else:
            # Amount is not given (unbounded read) so we must check self.length
            if self.length is None:
                s = check.isinstance((yield ReadIo(None)), bytes)

            else:
                try:
                    s = yield from self._safe_read(self.length)
                except IncompleteReadError:
                    self._close_conn()
                    raise

                self.length = 0

            self._close_conn()        # we read everything
            return s

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
        check.not_equal(self.chunked, _UNKNOWN)
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
        if self._closed or self._method == 'HEAD':
            return b''

        if self.chunked:
            return self._peek_chunked(n)

        # return self.fp.peek(n)
        raise NotImplementedError

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
        if self.fp is None or self._method == 'HEAD':
            return b''

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


class HttpConnection:
    """
    HTTPConnection goes through a number of "states", which define when a client may legally make another request or
    fetch the response for a particular request. This diagram details these state transitions:

        (null)
          |
          | HTTPConnection()
          v
        Idle
          |
          | put_request()
          v
        Request-started
          |
          | ( put_header() )*  end_headers()
          v
        Request-sent
          |______________________________
          |                              | get_response() raises
          | response = get_response()     | ConnectionError
          v                              v
        Unread-response                Idle
        [Response-headers-read]
          |_____________________
          |                     |
          | response.read()     | put_request()
          v                     v
        Idle                  Req-started-unread-response
                         ______/|
                       /        |
       response.read() |        | ( put_header() )*  end_headers()
                       v        v
           Request-started    Req-sent-unread-response
                                |
                                | response.read()
                                v
                              Request-sent

    This diagram presents the following rules:
      -- a second request may not be started until {response-headers-read}
      -- a response [object] cannot be retrieved until {request-sent}
      -- there is no differentiation between an unread response body and a
         partially read response body

    Logical State                _state       _response
    -------------                -------      ----------
    Idle                         IDLE         None
    Request-started              REQ_STARTED  None
    Request-sent                 REQ_SENT     None
    Unread-response              IDLE         <response_class>
    Req-started-unread-response  REQ_STARTED  <response_class>
    Req-sent-unread-response     REQ_SENT     <response_class>
    """

    _http_version = 11
    _http_version_str = 'HTTP/1.1'

    default_port = HTTP_PORT

    class _NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise NotImplementedError

    class _State(enum.Enum):
        IDLE = 'Idle'
        REQ_STARTED = 'Request-started'
        REQ_SENT = 'Request-sent'

    def __init__(
            self,
            host: str,
            port: ta.Optional[int] = None,
            *,
            timeout: ta.Union[float, ta.Type[_NOT_SET], None] = _NOT_SET,
            source_address: ta.Optional[str] = None,
            block_size: int = 8192,
            auto_open: bool = True,
    ) -> None:
        super().__init__()

        self._timeout = timeout
        self._source_address = source_address
        self._block_size = block_size
        self._auto_open = auto_open

        self._connected = False
        self._buffer: ta.List[bytes] = []
        self._response: ta.Optional[HttpResponse] = None
        self._state = self._State.IDLE
        self._method: ta.Optional[str] = None

        self._tunnel_host: ta.Optional[str] = None
        self._tunnel_port: ta.Optional[int] = None
        self._tunnel_headers: ta.Dict[str, str] = {}
        self._raw_proxy_headers: ta.Optional[ta.Sequence[bytes]] = None

        (self._host, self._port) = self._get_hostport(host, port)

        HttpClientValidation.validate_host(self._host)

    #

    def _get_hostport(self, host: str, port: ta.Optional[int]) -> ta.Tuple[str, int]:
        if port is None:
            i = host.rfind(':')
            j = host.rfind(']')  # ipv6 addresses have [...]
            if i > j:
                try:
                    port = int(host[i+1:])
                except ValueError:
                    if host[i+1:] == '':  # http://foo.com:/ == http://foo.com/
                        port = self.default_port
                    else:
                        raise InvalidUrlError(f"non-numeric port: '{host[i+1:]}'") from None
                host = host[:i]
            else:
                port = self.default_port

        if host and host[0] == '[' and host[-1] == ']':
            host = host[1:-1]

        return (host, port)

    def _wrap_ipv6(self, ip: bytes) -> bytes:
        if b':' in ip and ip[0] != b'['[0]:
            return b'[' + ip + b']'
        return ip

    #

    def set_tunnel(
            self,
            host: str,
            port: ta.Optional[int] = None,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        """
        Set up host and port for HTTP CONNECT tunnelling.

        In a connection that uses HTTP CONNECT tunnelling, the host passed to the constructor is used as a proxy server
        that relays all communication to the endpoint passed to `set_tunnel`. This done by sending an HTTP CONNECT
        request to the proxy server when the connection is established.

        This method must be called before the HTTP connection has been established.

        The headers argument should be a mapping of extra HTTP headers to send with the CONNECT request.

        As HTTP/1.1 is used for HTTP CONNECT tunnelling request, as per the RFC
        (https://tools.ietf.org/html/rfc7231#section-4.3.6), a HTTP Host: header must be provided, matching the
        authority-form of the request target provided as the destination for the CONNECT request. If a HTTP Host: header
        is not provided via the headers argument, one is generated and transmitted automatically.
        """

        if self._connected:
            raise RuntimeError("Can't set up tunnel for established connection")

        self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)

        if headers:
            self._tunnel_headers = dict(headers)
        else:
            self._tunnel_headers.clear()

        if not any(header.lower() == 'host' for header in self._tunnel_headers):
            encoded_host = self._tunnel_host.encode('idna').decode('ascii')
            self._tunnel_headers['Host'] = f'{encoded_host}:{self._tunnel_port:d}'

    def _tunnel(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        connect = b'CONNECT %s:%d %s\r\n' % (
            self._wrap_ipv6(check.not_none(self._tunnel_host).encode('idna')),
            check.not_none(self._tunnel_port),
            self._http_version_str.encode('ascii'),
        )
        headers = [connect]
        for header, value in self._tunnel_headers.items():
            headers.append(f'{header}: {value}\r\n'.encode('latin-1'))
        headers.append(b'\r\n')

        # Making a single send() call instead of one per line encourages the host OS to use a more optimal packet size
        # instead of potentially emitting a series of small packets.
        yield from self.send(b''.join(headers))
        del headers

        response = HttpResponse(method=self._method)
        try:
            # FIXME
            (version, code, message) = yield from response._read_status()  # noqa

            self._raw_proxy_headers = yield from _read_headers()

            if code != http.HTTPStatus.OK:
                yield from self.close()
                raise OSError(f'Tunnel connection failed: {code} {message.strip()}')

        finally:
            response.close()

    def get_proxy_response_headers(self) -> ta.Optional[email.message.Message]:
        """
        Returns a dictionary with the headers of the response received from the proxy server to the CONNECT request sent
        to set the tunnel.

        If the CONNECT request was not sent, the method returns None.
        """

        return (
            _parse_header_lines(self._raw_proxy_headers)
            if self._raw_proxy_headers is not None
            else None
        )

    #

    def connect(self) -> ta.Generator[Io, None, None]:
        """Connect to the host and port specified in __init__."""

        if self._connected:
            return

        check.none((yield ConnectIo(
            ((self._host, self._port),),
            dict(
                source_address=self._source_address,
                **(dict(timeout=self._timeout) if self._timeout is not self._NOT_SET else {}),  # type: ignore
            ),
        )))

        self._connected = True

        if self._tunnel_host:
            yield from self._tunnel()

    #

    def close(self) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """Close the connection to the HTTP server."""

        self._state = self._State.IDLE

        try:
            if self._connected:
                yield CloseIo()   # close it manually... there may be other refs
                self._connected = False

        finally:
            response = self._response
            if response:
                self._response = None
                response.close()

    #

    @staticmethod
    def _is_text_io(stream: ta.Any) -> bool:
        """Test whether a file-like object is a text or a binary stream."""

        return isinstance(stream, io.TextIOBase)

    def send(self, data: ta.Any) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """
        Send `data' to the server. ``data`` can be a string object, a bytes object, an array object, a file-like object
        that supports a .read() method, or an iterable object.
        """

        if not self._connected:
            if self._auto_open:
                yield from self.connect()
            else:
                raise NotConnectedError

        check.state(self._connected)

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

    #

    def put_request(
            self,
            method: str,
            url: str,
            *,
            skip_host: bool = False,
            skip_accept_encoding: bool = False,
    ) -> None:
        """
        Send a request to the server.

        `method' specifies an HTTP request method, e.g. 'GET'.
        `url' specifies the object being requested, e.g. '/index.html'.
        `skip_host' if True does not add automatically a 'Host:' header
        `skip_accept_encoding' if True does not add automatically an 'Accept-Encoding:' header
        """

        # if a prior response has been completed, then forget about it.
        if self._response and self._response.isclosed():
            self._response = None

        # in certain cases, we cannot issue another request on this connection.
        # this occurs when:
        #   1) we are in the process of sending a request. (_CS_REQ_STARTED)
        #   2) a response to a previous request has signalled that it is going to close the connection upon completion.
        #   3) the headers for the previous response have not been read, thus we cannot determine whether point (2) is
        #      true. (_CS_REQ_SENT)
        #
        # if there is no prior response, then we can request at will.
        #
        # if point (2) is true, then we will have passed the socket to the response (effectively meaning, "there is no
        # prior response"), and will open a new one when a new request is made.
        #
        # Note: if a prior response exists, then we *can* start a new request. We are not allowed to begin fetching the
        #       response to this new request, however, until that prior response is complete.
        #
        if self._state == self._State.IDLE:
            self._state = self._State.REQ_STARTED
        else:
            raise CannotSendRequestError(self._state)

        HttpClientValidation.validate_method(method)

        # Save the method for use later in the response phase
        self._method = method

        url = url or '/'
        HttpClientValidation.validate_path(url)

        request = f'{method} {url} {self._http_version_str}'

        self._output(self._encode_request(request))

        if self._http_version == 11:
            # Issue some standard headers for better HTTP/1.1 compliance

            if not skip_host:
                # this header is issued *only* for HTTP/1.1 connections. more specifically, this means it is only issued
                # when the client uses the new HTTPConnection() class. backwards-compat clients will be using HTTP/1.0
                # and those clients may be issuing this header themselves. we should NOT issue it twice; some web
                # servers (such as Apache) barf when they see two Host: headers

                # If we need a non-standard port,include it in the header. If the request is going through a proxy, but
                # the host of the actual URL, not the host of the proxy.
                netloc = ''
                if url.startswith('http'):
                    netloc = urllib.parse.urlsplit(url).netloc

                if netloc:
                    try:
                        netloc_enc = netloc.encode('ascii')
                    except UnicodeEncodeError:
                        netloc_enc = netloc.encode('idna')
                    self.put_header('Host', _strip_ipv6_iface(netloc_enc))
                else:
                    if self._tunnel_host:
                        host = self._tunnel_host
                        port = self._tunnel_port
                    else:
                        host = self._host
                        port = self._port

                    try:
                        host_enc = host.encode('ascii')
                    except UnicodeEncodeError:
                        host_enc = host.encode('idna')

                    # As per RFC 273, IPv6 address should be wrapped with [] when used as Host header
                    host_enc = self._wrap_ipv6(host_enc)
                    if ':' in host:
                        host_enc = _strip_ipv6_iface(host_enc)

                    if port == self.default_port:
                        self.put_header('Host', host_enc)
                    else:
                        self.put_header('Host', f"{host_enc.decode('ascii')}:{port}")

            # NOTE: we are assuming that clients will not attempt to set these headers since *this* library must deal
            # with the consequences. this also means that when the supporting libraries are updated to recognize other
            # forms, then this code should be changed (removed or updated).

            # we only want a Content-Encoding of "identity" since we don't support encodings such as x-gzip or
            # x-deflate.
            if not skip_accept_encoding:
                self.put_header('Accept-Encoding', 'identity')

            # we can accept "chunked" Transfer-Encodings, but no others
            # NOTE: no TE header implies *only* "chunked"
            #self.put_header('TE', 'chunked')

            # if TE is supplied in the header, then it must appear in a Connection header.
            #self.put_header('Connection', 'TE')

        else:
            # For HTTP/1.0, the server will assume "not chunked"
            pass

    def _encode_request(self, request: str) -> bytes:
        # ASCII also helps prevent CVE-2019-9740.
        return request.encode('ascii')

    #

    def put_header(self, header: ta.Union[str, bytes], *values: ta.Union[bytes, str, int]) -> None:
        """
        Send a request header line to the server.

        For example: h.put_header('Accept', 'text/html')
        """

        if self._state != self._State.REQ_STARTED:
            raise CannotSendHeaderError

        if hasattr(header, 'encode'):
            bh = header.encode('ascii')
        else:
            bh = header

        HttpClientValidation.validate_header_name(bh)

        bvs = []
        for one_value in values:
            if hasattr(one_value, 'encode'):
                bv = one_value.encode('latin-1')
            elif isinstance(one_value, int):
                bv = str(one_value).encode('ascii')
            else:
                bv = one_value

            HttpClientValidation.validate_header_value(bv)
            bvs.append(bv)

        value = b'\r\n\t'.join(bvs)
        bh = bh + b': ' + value
        self._output(bh)

    def end_headers(
            self,
            message_body: ta.Optional[ta.Any] = None,
            *,
            encode_chunked: bool = False,
    ) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """
        Indicate that the last header line has been sent to the server.

        This method sends the request to the server. The optional message_body argument can be used to pass a message
        body associated with the request.
        """

        if self._state == self._State.REQ_STARTED:
            self._state = self._State.REQ_SENT
        else:
            raise CannotSendHeaderError

        yield from self._send_output(message_body, encode_chunked=encode_chunked)

    #

    def request(
            self,
            method: str,
            url: str,
            body: ta.Optional[ta.Any] = None,
            headers: ta.Optional[ta.Mapping[str, str]] = None,
            *,
            encode_chunked: bool = False,
    ) -> ta.Generator[Io, ta.Optional[bytes], None]:
        """Send a complete request to the server."""

        yield from self._send_request(method, url, body, dict(headers or {}), encode_chunked)

    @staticmethod
    def _get_content_length(
            body: ta.Optional[ta.Any],
            method: str,
    ) -> ta.Optional[int]:
        """
        Get the content-length based on the body.

        If the body is None, we set Content-Length: 0 for methods that expect a body (RFC 7230, Section 3.3.2). We also
        set the Content-Length for any method if the body is a str or bytes-like object and not a file.
        """

        if body is None:
            # do an explicit check for not None here to distinguish between unset and set but empty
            if method.upper() in _METHODS_EXPECTING_BODY:
                return 0
            else:
                return None

        if hasattr(body, 'read'):
            # file-like object.
            return None

        try:
            # does it implement the buffer protocol (bytes, bytearray, array)?
            mv = memoryview(body)
            return mv.nbytes
        except TypeError:
            pass

        if isinstance(body, str):
            return len(body)

        return None

    def _send_request(
            self,
            method: str,
            url: str,
            body: ta.Optional[ta.Any],
            headers: ta.Mapping[str, str],
            encode_chunked: bool,
    ) -> ta.Generator[Io, ta.Optional[bytes], None]:
        # Honor explicitly requested Host: and Accept-Encoding: headers.
        header_names = frozenset(k.lower() for k in headers)
        skips = {}
        if 'host' in header_names:
            skips['skip_host'] = True
        if 'accept-encoding' in header_names:
            skips['skip_accept_encoding'] = True

        self.put_request(method, url, **skips)

        # chunked encoding will happen if HTTP/1.1 is used and either the caller passes encode_chunked=True or the
        # following conditions hold:
        # 1. content-length has not been explicitly set
        # 2. the body is a file or iterable, but not a str or bytes-like
        # 3. Transfer-Encoding has NOT been explicitly set by the caller

        if 'content-length' not in header_names:
            # only chunk body if not explicitly set for backwards compatibility, assuming the client code is already
            # handling the chunking
            if 'transfer-encoding' not in header_names:
                # if content-length cannot be automatically determined, fall back to chunked encoding
                encode_chunked = False
                content_length = self._get_content_length(body, method)
                if content_length is None:
                    if body is not None:
                        encode_chunked = True
                        self.put_header('Transfer-Encoding', 'chunked')
                else:
                    self.put_header('Content-Length', str(content_length))
        else:
            encode_chunked = False

        for hdr, value in headers.items():
            self.put_header(hdr, value)

        if isinstance(body, str):
            # RFC 2616 Section 3.7.1 says that text default has a default charset of iso-8859-1.
            body = _encode(body, 'body')

        yield from self.end_headers(body, encode_chunked=encode_chunked)

    def get_response(self) -> ta.Generator[Io, ta.Optional[bytes], HttpResponse]:
        """
        Get the response from the server.

        If the HTTPConnection is in the correct state, returns an instance of HttpResponse or of whatever object is
        returned by the response_class variable.

        If a request has not been sent or if a previous response has not be handled, ResponseNotReady is raised. If the
        HTTP response indicates that the connection should be closed, then it will be closed before the response is
        returned. When the connection is closed, the underlying socket is closed.
        """

        # if a prior response has been completed, then forget about it.
        if self._response and self._response.isclosed():
            self._response = None

        # if a prior response exists, then it must be completed (otherwise, we cannot read this response's header to
        # determine the connection-close behavior)
        #
        # NOTE: if a prior response existed, but was connection-close, then the socket and response were made
        # independent of this HTTPConnection object since a new request requires that we open a whole new connection
        #
        # this means the prior response had one of two states:
        #   1) will_close: this connection was reset and the prior socket and response operate independently
        #   2) persistent: the response was retained and we await its isclosed() status to become true.
        if self._state != self._State.REQ_SENT or self._response:
            raise ResponseNotReadyError(self._state)

        response = HttpResponse(method=self._method)

        try:
            try:
                yield from response.begin()
            except ConnectionError:
                yield from self.close()
                raise

            check.not_equal(response.will_close, _UNKNOWN)
            self._state = self._State.IDLE

            if response.will_close:
                # this effectively passes the connection to the response
                yield from self.close()
            else:
                # remember this, so we can tell when it is complete
                self._response = response

            return response

        except:
            response.close()
            raise


def _main3() -> None:
    import urllib.request
    req = urllib.request.Request('https://www.baidu.com')
    with urllib.request.urlopen(req) as resp:  # noqa
        print(resp.read())


def _main2() -> None:
    conn_cls = __import__('http.client').client.HTTPConnection

    url = 'www.example.com'
    conn = conn_cls(url)

    conn.request('GET', '/')
    r1 = conn.get_response() if hasattr(conn, 'get_response') else conn.getresponse()  # noqa
    print((r1.status, r1.reason))

    # data1 = r1.read()

    while chunk := r1.read(200):
        print(repr(chunk))


def _main() -> None:
    conn_cls = HttpConnection

    url = 'www.example.com'
    conn = conn_cls(url)

    sock: ta.Optional[socket.socket] = None
    sock_file: ta.Optional = None

    def handle_io(o: Io) -> ta.Any:
        nonlocal sock
        nonlocal sock_file

        if isinstance(o, ConnectIo):
            check.none(sock)
            sock = socket.create_connection(*o.args, **o.kwargs)

            # Might fail in OSs that don't implement TCP_NODELAY
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except OSError as e:
                if e.errno != errno.ENOPROTOOPT:
                    raise

            sock_file = sock.makefile('rb')

            return None

        elif isinstance(o, CloseIo):
            check.not_none(sock).close()
            return None

        elif isinstance(o, WriteIo):
            check.not_none(sock).sendall(o.data)
            return None

        elif isinstance(o, ReadIo):
            if (sz := o.sz) is not None:
                return check.not_none(sock_file).read(sz)
            else:
                return check.not_none(sock_file).read()

        elif isinstance(o, ReadLineIo):
            return check.not_none(sock_file).readline(o.sz)

        else:
            raise TypeError(o)

    resp: ta.Optional[HttpResponse] = None

    def get_resp():
        nonlocal resp
        resp = yield from conn.get_response()

    def print_resp():
        d = yield from check.not_none(resp).read()
        print(d)

    for f in [
        conn.connect,
        lambda: conn.request('GET', '/'),
        get_resp,
        print_resp,
        conn.close,
    ]:
        g = f()
        i = None
        while True:
            try:
                o = g.send(i)
            except StopIteration:
                break
            i = handle_io(o)

    # conn.request('GET', '/')
    # r1 = conn.get_response() if hasattr(conn, 'get_response') else conn.getresponse()  # noqa
    # print((r1.status, r1.reason))
    #
    # # data1 = r1.read()
    #
    # while chunk := r1.read(200):
    #     print(repr(chunk))


if __name__ == '__main__':
    _main()
