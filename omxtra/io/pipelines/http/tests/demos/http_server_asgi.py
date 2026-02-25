import asyncio
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class AsgiSpec:
    app: ta.Any
    host: str = '127.0.0.1'
    port: int = 8087


##


async def a_serve_asgi_pipeline(spec: AsgiSpec) -> None:
    raise NotImplementedError


def serve_asgi_pipeline(spec: AsgiSpec) -> None:
    asyncio.run(a_serve_asgi_pipeline(spec))


##


def serve_asgi_uvicorn(spec: AsgiSpec) -> None:
    import uvicorn  # noqa

    server = uvicorn.Server(uvicorn.Config(
        spec.app,
        host=spec.host,
        port=spec.port,
    ))

    asyncio.run(server.serve())


##


async def ping_app(scope, receive, send):
    if scope['type'] != 'http':
        return

    method = scope.get('method')
    path = scope.get('path')

    if method == 'GET' and path == '/ping':
        body = b'pong'
        status = 200
    else:
        body = b'not found'
        status = 404

    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', str(len(body)).encode('ascii')),
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


##


def _main() -> None:
    ping_spec = AsgiSpec(ping_app)

    serve_asgi_uvicorn(ping_spec)
    # serve_asgi_pipeline(ping_spec)


if __name__ == '__main__':
    _main()
