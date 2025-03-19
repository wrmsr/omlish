import typing as ta

from omlish import check
from omlish.asyncs.buffers import AsyncBufferedReader


##


def format_http_framed_message(
        content: bytes,
        headers: ta.Mapping[str, str] | None = None,
        *,
        header_encoding: str = 'ascii',
) -> bytes:
    headers = dict(headers or {})

    if 'Content-Length' not in headers:
        headers['Content-Length'] = str(len(content))

    return b'\r\n'.join([
        *[
            b'%s: %s' % (k.encode(header_encoding), v.encode(header_encoding))
            for k, v in headers.items()
        ],
        b'',
        content,
    ])


async def read_http_framed_message(
        reader: AsyncBufferedReader,
        *,
        header_encoding: str = 'ascii',
        canceller: ta.Callable[[], bool] | None = None,
) -> tuple[bytes, dict[str, str]]:
    headers: dict[str, str] = {}

    while True:
        raw_line = await reader.read_until(b'\n', canceller=canceller)
        if not raw_line:
            raise EOFError

        check.state(raw_line.endswith(b'\r\n'))
        line = raw_line[:-2].decode(header_encoding)
        if not line:
            break

        key, value = line.split(': ', 1)
        headers[key.lower()] = value

    content_length = int(headers['content-length'])
    content = await reader.read_exact(content_length, canceller=canceller)
    check.equal(len(content), content_length)

    return (content, headers)
