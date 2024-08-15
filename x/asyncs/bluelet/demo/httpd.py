"""A simple Web server built with Bluelet to support concurrent requests in a single OS thread."""
import mimetypes
import os
import sys
import typing as ta

from .. import bluelet as bl


ROOT = '.'
INDEX_FILENAME = 'index.html'


def parse_request(lines):
    """Parse an HTTP request."""

    method, path, version = lines.pop(0).split(None, 2)
    headers = {}
    for line in lines:
        if not line:
            continue
        key, value = line.split(b': ', 1)
        headers[key] = value
    return method, path, headers


def mime_type(filename):
    """Return a reasonable MIME type for the file or text/plain as a fallback."""

    mt, _ = mimetypes.guess_type(filename)
    if mt:
        return mt
    else:
        return 'text/plain'


def respond(method, path, headers):
    """Generate an HTTP response for a parsed request."""

    # Remove query string, if any.
    if b'?' in path:
        path, query = path.split(b'?', 1)
    path = path.decode('utf8')

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
        files = []
        for name in sorted(os.listdir(filename), key=lambda n: (not os.path.isdir(n), n)):
            files.append(f'<li><a href="{name}">{"/" if os.path.isdir(name) else ""}{name}</a></li>')
        html = f'<html><head><title>{path}</title></head><body><h1>{path}</h1><ul>{"".join(files)}</ul></body></html>'
        return (
            '200 OK',
            {'Content-Type': 'text/html'},
            html.encode('utf8'),
        )

    elif os.path.exists(filename):
        # Send file contents.
        with open(filename, 'rb') as f:
            return '200 OK', {'Content-Type': mime_type(filename)}, f.read()

    else:
        # Not found.
        print('Not found.')
        return (
            '404 Not Found',
            {'Content-Type': 'text/html'},
            b'<html><head><title>404 Not Found</title></head><body><h1>Not found.</h1></body></html>',
        )


def webrequest(conn: bl.Connection) -> ta.Generator[bl.Event, ta.Any, None]:
    """A Bluelet coroutine implementing an HTTP server."""

    # Get the HTTP request.
    request = []
    while True:
        line = (yield conn.readline(b'\r\n')).strip()
        if not line:
            # End of headers.
            break
        request.append(line)

    # Make sure a request was sent.
    if not request:
        return

    # Parse and log the request and get the response values.
    method, path, headers = parse_request(request)
    print('%s %s' % (method, path))
    status, headers, content = respond(method, path, headers)

    # Send response.
    yield conn.sendall(f'HTTP/1.1 {status}\r\n'.encode('utf8'))
    for key, value in headers.items():
        yield conn.sendall(f'{key}: {value}\r\n'.encode('utf8'))
    yield conn.sendall(b'\r\n')
    yield conn.sendall(content)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT = os.path.expanduser(sys.argv[1])
    print('http://127.0.0.1:8000/')
    bl.run(bl.server('', 8000, webrequest))
