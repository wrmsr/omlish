import typing as ta

from omdev.cache import data as dcache
from omlish import check
from omlish import lang
from omlish.io.pipelines.asyncs import AsyncIoPipelineMessages  # noqa


##


async def serve_resource(
        send: ta.Callable,
        name: str,
        content_type: str = 'text/plain',
) -> None:
    body = check.not_none(lang.get_relative_resources('resources', globals=globals()).get(name)).read_bytes()

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', content_type.encode('ascii')),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def serve_data_cache_url(
        send: ta.Callable,
        url: str,
        content_type: str = 'text/plain',
) -> None:
    file_path = dcache.default().get(dcache.UrlSpec(url))

    with open(file_path, 'rb') as f:
        body = f.read()

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', content_type.encode('ascii')),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def serve_not_found(send: ta.Callable) -> None:
    body = b'not found'

    await send({
        'type': 'http.response.start',
        'status': 404,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })
