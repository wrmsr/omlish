# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import json
import time
import typing as ta

from omdev.cache import data as dcache
from omdev.home.secrets import install_env_secrets
from omlish import check
from omlish import lang
from omlish.http.pipelines.servers.apps.asgi import AsgiHandler
from omlish.http.pipelines.servers.apps.asgi import AsgiSpec
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from omlish.http.pipelines.servers.requests import IoPipelineHttpRequestDecoder
from omlish.http.pipelines.servers.responses import IoPipelineHttpResponseEncoder
from omlish.io.pipelines.asyncs import AsyncIoPipelineMessages  # noqa
from omlish.io.pipelines.core import IoPipeline
from omlish.io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from ommlds import minichain as mc

from .chat import ChatClient
from .chat import MockChatClient


##


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        drv = SimpleAsyncioStreamIoPipelineDriver(
            IoPipeline.Spec(
                [
                    IoPipelineHttpRequestDecoder(),
                    IoPipelineHttpRequestAggregatorDecoder(),
                    IoPipelineHttpResponseEncoder(),
                    AsgiHandler(spec.app),
                ],
            ).update_config(
                # raise_immediately=True,
            ),
            reader,
            writer,
        )

        await drv.run()

    srv = await asyncio.start_server(_handle_client, spec.host, spec.port)
    async with srv:
        await srv.serve_forever()


def serve_asgi_pipeline(spec: AsgiSpec) -> None:
    asyncio.run(a_serve_asgi_pipeline(spec))


##


async def _serve_resource(
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


async def _serve_data_cache_url(
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


async def _serve_not_found(send: ta.Callable) -> None:
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


_RESOURCE_ROUTES: ta.Mapping[str, tuple[str, str]] = {
    '/': ('index.html', 'text/html'),

    '/index.css': ('index.css', 'text/css'),

    '/sse-decoder.js': ('sse-decoder.js', 'application/javascript'),
    '/chat-app.js': ('chat-app.js', 'application/javascript'),
}

_DATA_CACHE_URL_ROUTES: ta.Mapping[str, tuple[str, str]] = {
    '/marked.js': ('https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js', 'application/javascript'),

    '/alpine.js': ('https://cdn.jsdelivr.net/npm/alpinejs@3.15.10/dist/cdn.min.js', 'application/javascript'),
}


CHAT_CLIENT: ChatClient = MockChatClient()


async def _serve_chat_completions(receive, send):
    ev = await receive()

    check.state(ev['type'] == 'http.request')
    check.state(not ev['more_body'])

    d = json.loads(ev['body'].decode('utf-8'))

    check.state(d['stream'])

    chat: list[mc.Message] = []
    for md in d['messages']:
        mr = md['role']
        ms = md['content']
        if not ms:
            continue
        if mr == 'user':
            chat.append(mc.UserMessage(ms))
        elif mr == 'assistant':
            chat.append(mc.AiMessage(ms))
        else:
            raise ValueError(mr)

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', b'text/event-stream'),
            (b'x-accel-buffering', b'no'),
        ],
    })

    llm = mc.registry_new(mc.ChatChoicesStreamService, 'openai')

    idx = 0

    async with (await llm.invoke(mc.ChatChoicesStreamRequest(chat))).v as st_resp:
        async for o in st_resp:
            deltas = check.single(o.choices).deltas
            for delta in deltas:
                cd = check.isinstance(delta, mc.ContentAiDelta)
                await send({
                    'type': 'http.response.body',
                    'body': ''.join([
                        f'data: ',
                        json.dumps(
                            {
                                'id': 'chatcmpl-mock',
                                'object': 'chat.completion.chunk',
                                'created': int(time.time()),
                                'model': d['model'],
                                'choices': [{
                                    'index': idx,
                                    'delta': {'content': check.isinstance(cd.c, str)},
                                    'finish_reason': None
                                }]
                            },
                        ),
                        '\n\n',
                    ]).encode('utf-8'),
                    'more_body': True,
                })
                idx += 1

    await send({
        'type': 'http.response.body',
        'body': ''.join([
            f'data: ',
            json.dumps(
                {
                    'id': 'chatcmpl-mock',
                    'object': 'chat.completion.chunk',
                    'created': int(time.time()),
                    'model': d['model'],
                    'choices': [{
                        'index': idx,
                        'delta': {},
                        'finish_reason': 'stop'
                    }]
                },
            ),
            '\n\n',
        ]).encode('utf-8'),
        'more_body': True,
    })
    idx += 1

    await send({
        'type': 'http.response.body',
        'body': 'data: [DONE]\n\n'.encode('utf-8'),
        'more_body': False,
    })


async def app(scope, receive, send):
    if scope['type'] != 'http':
        return

    method = scope.get('method')
    path = scope.get('path')

    if method == 'GET' and (rsrc_rt := _RESOURCE_ROUTES.get(path)) is not None:
        await _serve_resource(send, *rsrc_rt)

    elif method == 'GET' and (dcu_rt := _DATA_CACHE_URL_ROUTES.get(path)) is not None:
        await _serve_data_cache_url(send, *dcu_rt)

    elif (method, path) == ('POST', '/v1/chat/completions'):
        await _serve_chat_completions(receive, send)

    else:
        await _serve_not_found(send)


##


def _main() -> None:
    install_env_secrets('openai_api_key')

    app_spec = AsgiSpec(app)

    serve_asgi_pipeline(app_spec)


if __name__ == '__main__':
    _main()
