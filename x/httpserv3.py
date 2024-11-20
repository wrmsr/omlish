"""
TODO:
 - SocketClientAddress family / tuple pairs
  + codification of https://docs.python.org/3/library/socket.html#socket-families
"""
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
import dataclasses as dc
import datetime
import email.utils
import html
import http.client
import http.server
import itertools
import socket
import socketserver
import sys
import time
import typing as ta

from omlish.http import consts as hc


SocketAddress: ta.TypeAlias = ta.Any


##


class SocketServerBaseRequestHandler_:  # noqa
    request: socket.socket
    client_address: SocketAddress
    server: socketserver.TCPServer


class SocketServerStreamRequestHandler_(SocketServerBaseRequestHandler_):  # noqa
    rbufsize: int
    wbufsize: int

    timeout: float | None

    disable_nagle_algorithm: bool

    connection: socket.socket
    rfile: ta.IO
    wfile: ta.IO


DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""

DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'


##


class BaseHTTPRequestHandler(
    socketserver.StreamRequestHandler,
    SocketServerStreamRequestHandler_,
):
    def __init__(
            self,
            request: socket.socket,
            client_address: SocketAddress,
            server: socketserver.TCPServer,
    ) -> None:
        super().__init__(
            request,
            client_address,
            server,
        )

    #

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    # The default request version. This only affects responses up until the point where the request line is parsed, so
    # it mainly decides what the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    default_request_version = 'HTTP/0.9'

    #

    command: str | None
    request_version: str
    close_connection: bool

    request_line: str
    path: str

    headers: http.client.HTTPMessage

    def parse_request(self) -> bool:
        self.command = None  # set in case of error on the first line
        self.request_version = self.default_request_version
        self.close_connection = True

        request_line = str(self.raw_request_line, 'iso-8859-1')
        request_line = request_line.rstrip('\r\n')
        self.request_line = request_line

        words = request_line.split()
        if len(words) == 0:
            return False

        if len(words) >= 3:  # Enough to determine protocol version
            version = words[-1]
            try:
                if not version.startswith('HTTP/'):
                    raise ValueError

                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split('.')

                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                if any(not component.isdigit() for component in version_number):
                    raise ValueError('non digit in http version')
                if any(len(component) > 10 for component in version_number):
                    raise ValueError('unreasonable length http version')
                version_number = int(version_number[0]), int(version_number[1])

            except (ValueError, IndexError):
                self.send_error(
                    http.HTTPStatus.BAD_REQUEST,
                    f'Bad request version ({version!r})',
                )
                return False

            if version_number >= (1, 1) and self.protocol_version >= 'HTTP/1.1':
                self.close_connection = False

            if version_number >= (2, 0):
                self.send_error(
                    http.HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    f'Invalid HTTP version ({base_version_number})',
                )
                return False

            self.request_version = version

        if not 2 <= len(words) <= 3:
            self.send_error(
                http.HTTPStatus.BAD_REQUEST,
                f'Bad request syntax ({request_line!r})',
            )
            return False

        command, path = words[:2]
        if len(words) == 2:
            self.close_connection = True
            if command != 'GET':
                self.send_error(
                    http.HTTPStatus.BAD_REQUEST,
                    f'Bad HTTP/0.9 request type ({command!r})',
                )
                return False

        self.command = command
        self.path = path

        # gh-87389: The purpose of replacing '//' with '/' is to protect against open redirect attacks possibly
        # triggered if the path starts with '//' because http clients treat //path as an absolute URI without scheme
        # (similar to http://path) rather than a path.
        if self.path.startswith('//'):
            self.path = '/' + self.path.lstrip('/')  # Reduce to a single /

        # Examine the headers and look for a Connection directive.
        try:
            self.headers = http.client.parse_headers(self.rfile)

        except http.client.LineTooLong as err:
            self.send_error(
                http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                'Line too long',
                str(err),
            )
            return False

        except http.client.HTTPException as err:
            self.send_error(
                http.HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                'Too many headers',
                str(err),
            )
            return False

        conn_type = self.headers.get('Connection', '')
        if conn_type.lower() == 'close':
            self.close_connection = True
        elif (
                conn_type.lower() == 'keep-alive' and
                self.protocol_version >= 'HTTP/1.1'
        ):
            self.close_connection = False

        # Examine the headers and look for an Expect directive
        expect = self.headers.get('Expect', '')
        if (
                expect.lower() == '100-continue' and
                self.protocol_version >= 'HTTP/1.1' and
                self.request_version >= 'HTTP/1.1'
        ):
            if not self.handle_expect_100():
                return False

        return True

    def handle_expect_100(self) -> bool:
        self.send_response_only(http.HTTPStatus.CONTINUE)
        self.end_headers()
        return True

    raw_request_line: bytes

    def handle_one_request(self) -> None:
        try:
            self.raw_request_line = self.rfile.readline(65537)

            if len(self.raw_request_line) > 65536:
                self.request_line = ''
                self.request_version = ''
                self.command = ''
                self.send_error(http.HTTPStatus.REQUEST_URI_TOO_LONG)
                return

            if not self.raw_request_line:
                self.close_connection = True
                return

            if not self.parse_request():
                # An error code has been sent, just exit
                return

            method_name = 'do_' + self.command
            if not hasattr(self, method_name):
                self.send_error(
                    http.HTTPStatus.NOT_IMPLEMENTED,
                    f'Unsupported method ({self.command!r})',
                )
                return

            method = getattr(self, method_name)
            method()
            self.wfile.flush() #actually send the response if not already done.

        except TimeoutError as e:
            # A read or a write timed out. Discard this connection
            self.log_error('Request timed out: %r', e)
            self.close_connection = True
            return

    def handle(self) -> None:
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    def send_error(self, code, message=None, explain=None) -> None:
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = '???', '???'
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg

        self.log_error('code %d, message %s', code, message)

        self.send_response(code, message)
        self.send_header('Connection', 'close')

        # Message body is omitted for cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        body = None
        if (
                code >= 200 and
                code not in (
                    http.HTTPStatus.NO_CONTENT,
                    http.HTTPStatus.RESET_CONTENT,
                    http.HTTPStatus.NOT_MODIFIED,
                )
        ):
            # HTML encode to prevent Cross Site Scripting attacks (see bug #1100201)
            content = (self.error_message_format % {
                'code': code,
                'message': html.escape(message, quote=False),
                'explain': html.escape(explain, quote=False)
            })
            body = content.encode('UTF-8', 'replace')
            self.send_header('Content-Type', self.error_content_type)
            self.send_header('Content-Length', str(len(body)))

        self.end_headers()

        if self.command != 'HEAD' and body:
            self.wfile.write(body)

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def send_response_only(self, code, message=None):
        if self.request_version != 'HTTP/0.9':
            if message is None:
                if code in self.responses:
                    message = self.responses[code][0]
                else:
                    message = ''

            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []

            line = f'{self.protocol_version} {int(code)} {message}\r\n'
            self._headers_buffer.append(line.encode('latin-1', 'strict'))

    def send_header(self, keyword, value):
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            line = f'{keyword}: {value}\r\n'
            self._headers_buffer.append(line.encode('latin-1', 'strict'))

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

    def end_headers(self):
        if self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b'\r\n')
            self.flush_headers()

    def flush_headers(self):
        if hasattr(self, '_headers_buffer'):
            self.wfile.write(b''.join(self._headers_buffer))
            self._headers_buffer = []

    def log_request(self, code='-', size='-'):
        if isinstance(code, http.HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s', self.request_line, str(code), str(size))

    def log_error(self, format, *args):
        self.log_message(format, *args)

    # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Control_codes
    _control_char_table = str.maketrans({
        c: fr'\x{c:02x}'
        for c in itertools.chain(range(0x20), range(0x7f,0xa0))
    })
    _control_char_table[ord('\\')] = r'\\'

    def log_message(self, format, *args):
        message = format % args
        sys.stderr.write(
            '%s - - [%s] %s\n' % (
                self.address_string(),
                self.log_date_time_string(),
                message.translate(self._control_char_table),
            ),
        )

    def version_string(self) -> str:
        return 'BaseHTTP/0.0'

    def date_time_string(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    def log_date_time_string(self) -> str:
        return datetime.datetime.now().ctime()

    def address_string(self) -> str:
        return self.client_address[0]

    protocol_version = 'HTTP/1.0'

    # hack to maintain backwards compatibility
    responses = {
        v: (v.phrase, v.description)
        for v in http.HTTPStatus.__members__.values()
    }


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        out = b'hi'

        self.send_response(http.HTTPStatus.OK)
        self.send_header(hc.HEADER_CONTENT_TYPE.decode(), hc.CONTENT_TYPE_TEXT.decode())
        self.send_header(hc.HEADER_CONTENT_LENGTH.decode(), str(len(out)))
        self.end_headers()
        self.wfile.write(out)


##


@dc.dataclass(frozen=True)
class AddrInfoArgs:
    host: str | None
    port: str | int | None
    family: socket.AddressFamily = socket.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket.AddressInfo = socket.AddressInfo(0)


def _get_best_family(*address) -> tuple[socket.AddressFamily, SocketAddress]:
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


##


def _main() -> None:
    port = 8000
    bind = None
    protocol = 'HTTP/1.0'

    ServerClass = http.server.ThreadingHTTPServer
    HandlerClass = SimpleHTTPRequestHandler

    ServerClass.address_family, addr = _get_best_family(bind, port)
    HandlerClass.protocol_version = protocol
    with ServerClass(addr, HandlerClass) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        print(f'Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)


if __name__ == '__main__':
    _main()
