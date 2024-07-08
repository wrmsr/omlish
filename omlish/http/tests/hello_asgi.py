import typing as ta

from ... import check


def app(scope):
    check.equal(scope['type'], 'http')  # Ignore anything other than HTTP

    async def asgi(receive, send):
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, World!',
        })

    return asgi


def _main() -> None:
    uvicorn: ta.Any = __import__('uvicorn')
    uvicorn.run(app, host='', port=8000)


if __name__ == '__main__':
    _main()
