from ..types import ASGIReceiveCallable
from ..types import ASGISendCallable
from ..types import Scope


SANITY_REQUEST_BODY = b'Hello Hypercorn'
SANITY_RESPONSE_BODY = b'Hello & Goodbye'


async def sanity_framework(
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
) -> None:
    body = b''
    if scope['type'] == 'websocket':
        await send({'type': 'websocket.accept'})

    while True:
        event = await receive()

        if event['type'] in {'http.disconnect', 'websocket.disconnect'}:
            break

        elif event['type'] == 'lifespan.startup':
            await send({'type': 'lifespan.startup.complete'})

        elif event['type'] == 'lifespan.shutdown':
            await send({'type': 'lifespan.shutdown.complete'})

        elif event['type'] == 'http.request' and event.get('more_body', False):
            body += event['body']

        elif event['type'] == 'http.request' and not event.get('more_body', False):
            body += event['body']
            assert body == SANITY_REQUEST_BODY
            response = SANITY_RESPONSE_BODY
            content_length = len(response)
            await send(
                {
                    'type': 'http.response.start',
                    'status': 200,
                    'headers': [(b'content-length', str(content_length).encode())],
                }
            )
            await send({'type': 'http.response.body', 'body': response, 'more_body': False})
            break

        elif event['type'] == 'websocket.receive':
            assert event['bytes'] == SANITY_REQUEST_BODY
            await send({'type': 'websocket.send', 'text': 'Hello & Goodbye'})
