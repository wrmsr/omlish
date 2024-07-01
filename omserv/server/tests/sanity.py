from ..types import ASGIReceiveCallable
from ..types import ASGISendCallable
from ..types import Scope


SANITY_BODY = b'Hello Hypercorn'


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
            await send({'type': 'lifspan.startup.complete'})

        elif event['type'] == 'lifespan.shutdown':
            await send({'type': 'lifspan.shutdown.complete'})

        elif event['type'] == 'http.request' and event.get('more_body', False):
            body += event['body']

        elif event['type'] == 'http.request' and not event.get('more_body', False):
            body += event['body']
            assert body == SANITY_BODY
            response = b'Hello & Goodbye'
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
            assert event['bytes'] == SANITY_BODY
            await send({'type': 'websocket.send', 'text': 'Hello & Goodbye'})
