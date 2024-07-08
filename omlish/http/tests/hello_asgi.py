"""
https://asgi.readthedocs.io/_/downloads/en/latest/pdf/

REQUEST_METHOD is the method
SCRIPT_NAME is root_path
PATH_INFO can be derived by stripping root_path from path
QUERY_STRING is query_string
CONTENT_TYPE can be extracted from headers
CONTENT_LENGTH can be extracted from headers
SERVER_NAME and SERVER_PORT are in server
REMOTE_HOST/REMOTE_ADDR and REMOTE_PORT are in client
SERVER_PROTOCOL is encoded in http_version
wsgi.url_scheme is scheme
wsgi.input is a StringIO based around the http.request messages
wsgi.errors is directed by the wrapper as needed
"""
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

    # import anyio
    # omserv: ta.Any = __import__('omserv.server')
    # anyio.run(omserv.server.serve, app, omserv.server.Config())


if __name__ == '__main__':
    _main()
