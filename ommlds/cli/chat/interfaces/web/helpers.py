import json
import typing as ta
import urllib.parse


##


def sse_bytes(event: str, data: ta.Any) -> bytes:
    return ''.join([
        f'event: {event}\n',
        f'data: {json.dumps(data, separators=(",", ":"))}\n',
        '\n',
    ]).encode('utf-8')


async def send_sse_headers(send: ta.Any) -> None:
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', b'text/event-stream'),
            (b'cache-control', b'no-cache'),
            (b'x-accel-buffering', b'no'),
        ],
    })


async def send_json(send: ta.Any, obj: ta.Any, *, status: int = 200) -> None:
    body = json.dumps(obj).encode('utf-8')

    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'application/json'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


def parse_query(scope: ta.Any) -> dict[str, str]:
    return dict(urllib.parse.parse_qsl((scope.get('query_string') or b'').decode('utf-8')))
