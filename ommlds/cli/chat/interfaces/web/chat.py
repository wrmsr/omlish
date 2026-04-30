import contextlib
import json
import time
import typing as ta

from omlish import check

from ..... import minichain as mc
from .types import ChatStreamer


##


class DefaultChatStreamer:
    async def __call__(self, chat: mc.Chat) -> ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]:
        @contextlib.asynccontextmanager
        async def outer() -> ta.Any:
            llm = mc.registry_new(mc.ChatChoicesStreamService, 'openai')

            async with (await llm.invoke(mc.ChatChoicesStreamRequest(chat))).v as st_resp:
                async def inner() -> ta.Any:
                    async for o in st_resp:
                        deltas = check.single(o.choices).deltas
                        for delta in deltas:
                            yield delta

                yield inner()

        return outer()


##


class ChatCompletionsHandler:
    def __init__(
            self,
            *,
            chat_streamer: ChatStreamer,
    ) -> None:
        super().__init__()

        self._chat_streamer = chat_streamer

    async def handle(self, receive, send):
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

        idx = 0

        async with (await self._chat_streamer(chat)) as deltas:
            async for delta in deltas:
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
                                    'finish_reason': None,
                                }],
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
                            'finish_reason': 'stop',
                        }],
                    },
                ),
                '\n\n',
            ]).encode('utf-8'),
            'more_body': True,
        })
        idx += 1

        await send({
            'type': 'http.response.body',
            'body': b'data: [DONE]\n\n',
            'more_body': False,
        })
