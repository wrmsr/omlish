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
"""
https://github.com/python/cpython/blob/9b335cc8104dd83a5a1343dc649d1f3606682098/Lib/http/client.py
"""
import abc
import collections.abc
import dataclasses as dc
import email.parser
import enum
import errno
import io
import socket
import typing as ta
import urllib.parse

from http import HTTPStatus
from http.client import HTTPException
from http.client import HTTPMessage
from http.client import HTTPResponse
from http.client import InvalidURL
from http.client import LineTooLong
from http.client import NotConnected
from http.client import CannotSendRequest
from http.client import CannotSendHeader
from http.client import ResponseNotReady

from omlish import check

from .validation import HttpClientValidation


##


class Io(abc.ABC):  # noqa
    pass


#

class AnyReadIo(Io):  # noqa
    pass


@dc.dataclass(frozen=True)
class ReadIo(AnyReadIo):
    sz: int


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


def _read_headers(fp: ta.IO) -> list[bytes]:
    """
    Reads potential header lines into a list from a file pointer.

    Length of line is limited by _MAX_LINE, and number of headers is limited by _MAX_HEADERS.
    """

    headers = []
    while True:
        line = fp.readline(_MAX_LINE + 1)
        if len(line) > _MAX_LINE:
            raise LineTooLong('header line')

        headers.append(line)
        if len(headers) > _MAX_HEADERS:
            raise HTTPException(f'got more than {_MAX_HEADERS} headers')

        if line in (b'\r\n', b'\n', b''):
            break

    return headers


def _parse_header_lines(header_lines: ta.Sequence[bytes]) -> HTTPMessage:
    """
    Parses only RFC2822 headers from header lines.

    email Parser wants to see strings rather than bytes. But a TextIOWrapper around self.rfile would buffer too many
    bytes from the stream, bytes which we later need to read as bytes. So we read the correct bytes here, as bytes, for
    email Parser to parse.
    """

    hstring = b''.join(header_lines).decode('iso-8859-1')
    return email.parser.Parser(_class=HTTPMessage).parsestr(hstring)


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
            port: int | None = None,
            *,
            timeout: float | None | type[_NOT_SET] = _NOT_SET,
            source_address: str | None = None,
            block_size: int = 8192,
            auto_open: bool = True,
    ) -> None:
        super().__init__()

        self._timeout = timeout
        self._source_address = source_address
        self._block_size = block_size
        self._auto_open = auto_open

        self._sock: socket.socket | None = None
        self._buffer: list[bytes] = []
        self._response: HTTPResponse | None = None
        self._state = self._State.IDLE
        self._method: str | None = None

        self._tunnel_host: str | None = None
        self._tunnel_port: int | None = None
        self._tunnel_headers: dict[str, str] = {}
        self._raw_proxy_headers: ta.Sequence[bytes] | None = None

        (self._host, self._port) = self._get_hostport(host, port)

        HttpClientValidation.validate_host(self._host)

        # This is stored as an instance variable to allow unit tests to replace it with a suitable mockup
        self._create_connection = socket.create_connection

    #

    def _get_hostport(self, host: str, port: int | None) -> tuple[str, int]:
        if port is None:
            i = host.rfind(':')
            j = host.rfind(']')         # ipv6 addresses have [...]
            if i > j:
                try:
                    port = int(host[i+1:])
                except ValueError:
                    if host[i+1:] == '': # http://foo.com:/ == http://foo.com/
                        port = self.default_port
                    else:
                        raise InvalidURL(f"non-numeric port: '{host[i+1:]}'") from None
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
            port: int | None = None,
            headers: ta.Mapping[str, str] | None = None,
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

        if self._sock:
            raise RuntimeError("Can't set up tunnel for established connection")

        self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)

        if headers:
            self._tunnel_headers = dict(headers)
        else:
            self._tunnel_headers.clear()

        if not any(header.lower() == 'host' for header in self._tunnel_headers):
            encoded_host = self._tunnel_host.encode('idna').decode('ascii')
            self._tunnel_headers['Host'] = f'{encoded_host}:{self._tunnel_port:d}'

    def _tunnel(self) -> None:
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
        self.send(b''.join(headers))
        del headers

        response = HTTPResponse(check.not_none(self._sock), method=self._method)
        try:
            # FIXME
            (version, code, message) = response._read_status()  # type: ignore  # noqa

            self._raw_proxy_headers = _read_headers(response.fp)

            if code != HTTPStatus.OK:
                self.close()
                raise OSError(f'Tunnel connection failed: {code} {message.strip()}')

        finally:
            response.close()

    def get_proxy_response_headers(self) -> HTTPMessage | None:
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

    def connect(self) -> None:
        """Connect to the host and port specified in __init__."""

        self._sock = self._create_connection(
            (self._host, self._port),
            source_address=self._source_address,
            **(dict(timeout=self._timeout) if self._timeout is not self._NOT_SET else {}),  # type: ignore
        )
        # Might fail in OSs that don't implement TCP_NODELAY
        try:
            self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        if self._tunnel_host:
            self._tunnel()

    #

    def close(self) -> None:
        """Close the connection to the HTTP server."""

        self._state = self._State.IDLE
        try:
            sock = self._sock
            if sock:
                self._sock = None
                sock.close()   # close it manually... there may be other refs
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

    def send(self, data: ta.Any) -> None:
        """
        Send `data' to the server. ``data`` can be a string object, a bytes object, an array object, a file-like object
        that supports a .read() method, or an iterable object.
        """

        if self._sock is None:
            if self._auto_open:
                self.connect()
            else:
                raise NotConnected

        sock = check.not_none(self._sock)

        if hasattr(data, 'read') :
            encode = self._is_text_io(data)
            while data_block := data.read(self._block_size):
                if encode:
                    data_block = data_block.encode('iso-8859-1')
                sock.sendall(data_block)
            return

        try:
            sock.sendall(data)
        except TypeError:
            if isinstance(data, collections.abc.Iterable):
                for d in data:
                    sock.sendall(d)
            else:
                raise TypeError(f'data should be a bytes-like object or an iterable, got {type(data)!r}') from None

    def _output(self, s: bytes) -> None:
        """
        Add a line of output to the current request buffer.

        Assumes that the line does *not* end with \\r\\n.
        """

        self._buffer.append(s)

    def _read_readable(self, readable: ta.IO | ta.TextIO) -> ta.Iterator[bytes]:
        while data := readable.read(self._block_size):
            if isinstance(data, str):
                yield data.encode('iso-8859-1')
            else:
                yield data

    def _send_output(
            self,
            message_body: ta.Any | None = None,
            encode_chunked: bool = False,
    ) -> None:
        """
        Send the currently buffered request and clear the buffer.

        Appends an extra \\r\\n to the buffer. A message_body may be specified, to be appended to the request.
        """

        self._buffer.extend((b'', b''))
        msg = b'\r\n'.join(self._buffer)
        del self._buffer[:]
        self.send(msg)

        chunks: ta.Iterable[bytes]
        if message_body is not None:
            # create a consistent interface to message_body
            if hasattr(message_body, 'read'):
                # Let file-like take precedence over byte-like.  This is needed to allow the current position of mmap'ed
                # files to be taken into account.
                chunks = self._read_readable(message_body)
            else:
                try:
                    # this is solely to check to see if message_body implements the buffer API.  it /would/ be easier to
                    # capture if PyObject_CheckBuffer was exposed to Python.
                    memoryview(message_body)
                except TypeError:
                    try:
                        chunks = iter(message_body)
                    except TypeError:
                        raise TypeError('message_body should be a bytes-like object or an iterable, got %r' % type(message_body))  # noqa
                else:
                    # the object implements the buffer interface and can be passed directly into socket methods
                    chunks = (message_body,)

            for chunk in chunks:
                if not chunk:
                    continue

                if encode_chunked and self._http_version == 11:
                    # chunked encoding
                    chunk = f'{len(chunk):X}\r\n'.encode('ascii') + chunk + b'\r\n'
                self.send(chunk)

            if encode_chunked and self._http_version == 11:
                # end chunked transfer
                self.send(b'0\r\n\r\n')

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
        #   1) we are in the process of sending a request.   (_CS_REQ_STARTED)
        #   2) a response to a previous request has signalled that it is going to close the connection upon completion.
        #   3) the headers for the previous response have not been read, thus we cannot determine whether point (2) is
        #      true.   (_CS_REQ_SENT)
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
            raise CannotSendRequest(self._state)

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

                # If we need a non-standard port,include it in the header.  If the request is going through a proxy, but
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

    def put_header(self, header: str | bytes, *values: bytes | str | int) -> None:
        """
        Send a request header line to the server.

        For example: h.put_header('Accept', 'text/html')
        """

        if self._state != self._State.REQ_STARTED:
            raise CannotSendHeader

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
            message_body: ta.Any | None = None,
            *,
            encode_chunked: bool = False,
    ) -> None:
        """Indicate that the last header line has been sent to the server.

        This method sends the request to the server.  The optional message_body argument can be used to pass a message
        body associated with the request.
        """

        if self._state == self._State.REQ_STARTED:
            self._state = self._State.REQ_SENT
        else:
            raise CannotSendHeader

        self._send_output(message_body, encode_chunked=encode_chunked)

    #

    def request(
            self,
            method: str,
            url: str,
            body: ta.Any | None = None,
            headers: ta.Mapping[str, str] | None = None,
            *,
            encode_chunked: bool = False,
    ) -> None:
        """Send a complete request to the server."""

        self._send_request(method, url, body, dict(headers or {}), encode_chunked)

    @staticmethod
    def _get_content_length(
            body: ta.Any | None,
            method: str,
    ) -> int | None:
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
            body: ta.Any | None,
            headers: ta.Mapping[str, str],
            encode_chunked: bool,
    ) -> None:
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

        self.end_headers(body, encode_chunked=encode_chunked)

    def get_response(self) -> HTTPResponse:
        """
        Get the response from the server.

        If the HTTPConnection is in the correct state, returns an instance of HTTPResponse or of whatever object is
        returned by the response_class variable.

        If a request has not been sent or if a previous response has not be handled, ResponseNotReady is raised.  If the
        HTTP response indicates that the connection should be closed, then it will be closed before the response is
        returned.  When the connection is closed, the underlying socket is closed.
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
            raise ResponseNotReady(self._state)

        response = HTTPResponse(check.not_none(self._sock), method=self._method)

        try:
            try:
                response.begin()
            except ConnectionError:
                self.close()
                raise

            check.not_equal(response.will_close, _UNKNOWN)
            self._state = self._State.IDLE

            if response.will_close:
                # this effectively passes the connection to the response
                self.close()
            else:
                # remember this, so we can tell when it is complete
                self._response = response

            return response

        except:
            response.close()
            raise


def _main() -> None:
    # import urllib.request
    # req = urllib.request.Request('https://www.baidu.com')
    # with urllib.request.urlopen(req) as resp:
    #     print(resp.read())

    conn = HttpConnection('www.example.com')

    conn.request('GET', '/')
    r1 = conn.get_response()
    print((r1.status, r1.reason))

    # data1 = r1.read()

    while chunk := r1.read(200):
        print(repr(chunk))


if __name__ == '__main__':
    _main()
