import json
import typing as ta
import uuid

from omlish import check

from ..... import minichain as mc
from .helpers import send_json


##


class UserInputHandler:
    def __init__(
            self,
            *,
            facade: mc.facades.Facade,
    ) -> None:
        super().__init__()

        self._facade = facade

    async def handle(self, scope: ta.Any, receive: ta.Any, send: ta.Any) -> None:
        ev = await receive()
        check.state(ev['type'] == 'http.request')

        body = ev['body']
        while ev.get('more_body'):
            ev = await receive()
            body += ev['body']

        d = json.loads(body.decode('utf-8'))
        text = check.non_empty_str(d['text'])

        input_uuid = uuid.uuid7()

        await self._facade.handle_user_input(text, input_uuid=input_uuid)

        await send_json(send, {'ok': True, 'input_uuid': str(input_uuid)})
