import json
import time

from omlish import check
from ommlds import minichain as mc


##


class ChatCompletionsHandler:
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
