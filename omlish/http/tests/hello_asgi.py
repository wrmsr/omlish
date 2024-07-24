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
from .. import consts


async def app(scope, receive, send):
    check.equal(scope['type'], 'http')  # Ignore anything other than HTTP

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [consts.HEADER_CONTENT_TYPE, consts.CONTENT_TYPE_TEXT_UTF8],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, World!',
    })


def _main() -> None:
    server = 'uvloop'
    server = 'omserv'

    match server:
        case 'uvloop':
            uvicorn: ta.Any = __import__('uvicorn')
            uvicorn.run(app, host='', port=8000)

        case 'omserv':
            import anyio
            omserv: ta.Any = __import__('omserv.server')
            anyio.run(omserv.server.serve, app, omserv.server.Config())

        case _:
            raise Exception(server)


if __name__ == '__main__':
    _main()
