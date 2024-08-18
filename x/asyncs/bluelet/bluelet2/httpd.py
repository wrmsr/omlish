"""A simple Web server built with Bluelet to support concurrent requests in a single OS thread."""
import dataclasses as dc
import mimetypes
import os
import sys
import typing as ta

from .. import bluelet2 as bl


ROOT = '.'
INDEX_FILENAME = 'index.html'


@dc.dataclass(frozen=True)
class Request:
    method: bytes
    path: bytes
    headers: ta.Mapping[bytes, bytes]


def parse_request(lines: ta.Sequence[bytes]) -> Request:
    """Parse an HTTP request."""

    method, path, version = lines[0].split(None, 2)
    headers: dict[bytes, bytes] = {}
    for line in lines[1:]:
        if not line:
            continue
        key, value = line.split(b': ', 1)
        headers[key] = value
    return Request(method, path, headers)


def mime_type(filename: str) -> str:
    """Return a reasonable MIME type for the file or text/plain as a fallback."""

    mt, _ = mimetypes.guess_type(filename)
    if mt:
        return mt
    else:
        return 'text/plain'


@dc.dataclass(frozen=True)
class Response:
    status: str
    headers: ta.Mapping[str, str]
    content: bytes


def respond(req: Request) -> Response:
    """Generate an HTTP response for a parsed request."""

    # Remove query string, if any.
    pathb = req.path
    if b'?' in pathb:
        pathb, query = pathb.split(b'?', 1)
    path = pathb.decode('utf8')

    # Strip leading / and add prefix.
    if path.startswith('/') and len(path) > 0:
        filename = path[1:]
    else:
        filename = path
    filename = os.path.join(ROOT, filename)

    # Expand to index file if possible.
    index_fn = os.path.join(filename, INDEX_FILENAME)
    if os.path.isdir(filename) and os.path.exists(index_fn):
        filename = index_fn

    if os.path.isdir(filename):
        # Directory listing.
        pfx = (path[1:] + '/') if len(path) > 1 else ''
        files = []
        for name in sorted(os.listdir(filename), key=lambda n: (not os.path.isdir(n), n)):
            files.append(f'<li><a href="{pfx}{name}">{"/" if os.path.isdir(name) else ""}{name}</a></li>')
        html = f'<html><head><title>{path}</title></head><body><h1>{path}</h1><ul>{"".join(files)}</ul></body></html>'
        return Response(
            '200 OK',
            {'Content-Type': 'text/html'},
            html.encode('utf8'),
        )

    elif os.path.exists(filename):
        # Send file contents.
        with open(filename, 'rb') as f:
            return Response(
                '200 OK',
                {'Content-Type': mime_type(filename)},
                f.read(),
            )

    else:
        # Not found.
        print('Not found.')
        return Response(
            '404 Not Found',
            {'Content-Type': 'text/html'},
            b'<html><head><title>404 Not Found</title></head><body><h1>Not found.</h1></body></html>',
        )


async def webrequest(conn: bl.Connection) -> bl.Coro:
    """A Bluelet coroutine implementing an HTTP server."""

    # Get the HTTP request.
    req_lines: list[bytes] = []
    while True:
        line = (await conn.readline(b'\r\n')).strip()
        if not line:
            # End of headers.
            break
        req_lines.append(line)

    # Make sure a request was sent.
    if not req_lines:
        return

    # Parse and log the request and get the response values.
    req = parse_request(req_lines)
    print('%r %r' % (req.method, req.path))
    resp = respond(req)

    # Send response.
    await conn.sendall(f'HTTP/1.1 {resp.status}\r\n'.encode('utf8'))
    for key, value in resp.headers.items():
        await conn.sendall(f'{key}: {value}\r\n'.encode('utf8'))
    await conn.sendall(b'\r\n')
    await conn.sendall(resp.content)


if __name__ == '__main__':
    async def ticker(delay: float = 3.):
        i = 0
        while True:
            await bl.sleep(delay)
            print(f'tick {i}')
            i += 1

    async def _main():
        await bl.spawn(bl.server('', 8000, webrequest))
        await bl.spawn(ticker())

    if len(sys.argv) > 1:
        ROOT = os.path.expanduser(sys.argv[1])

    print('http://127.0.0.1:8000/')
    bl.run(_main())
