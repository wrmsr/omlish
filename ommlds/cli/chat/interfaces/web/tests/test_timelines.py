"""
The browser-is-just-another-projector proof: drive the real web ChatApp's ASGI handlers directly (real injector chain,
real registry backend, real driver+timeline) - POST /input, stream GET /timeline SSE - then *reconstruct the
conversation from the wire bytes alone* (unmarshal window + events into a TimelineProjection) and assert it equals the
server's live state. Plus paged scrollback over the wire via GET /timeline/before.
"""
import asyncio
import json

import pytest

from omlish import inject as inj
from omlish import marshal as msh

from ...... import minichain as mc
from ......minichain.facades.timelines.tests.test_manager import canon_items
from .....backends.configs import BackendConfig
from .....inject import bind_main
from ....configs import ChatConfig
from ....drivers.configs import DriverConfig
from ....drivers.state.configs import StateConfig
from ..app import ChatApp
from ..configs import WebInterfaceConfig


##


def _chat_cfg(script: mc.ChatScript) -> ChatConfig:
    return ChatConfig(
        driver=DriverConfig(
            ai=mc.drivers.AiConfig(stream=True),
            backend=BackendConfig(
                backend='scripted',
                # A shared cursor: the registry path instantiates a fresh backend per invocation.
                configs=[mc.ScriptedChatCursor(mc.ChatScriptCursor(script))],
            ),
            state=StateConfig(new=True),
        ),
        interface=WebInterfaceConfig(),
    )


class _AsgiCall:
    """A hand-rolled ASGI exchange: queue-fed receive, list-collecting send."""

    def __init__(self, method: str, path: str, *, query_string: bytes = b'', body: bytes | None = None) -> None:
        super().__init__()

        self.scope = {
            'type': 'http',
            'method': method,
            'path': path,
            'query_string': query_string,
        }

        self.receive_queue: asyncio.Queue = asyncio.Queue()
        if body is not None:
            self.receive_queue.put_nowait({'type': 'http.request', 'body': body, 'more_body': False})

        self.sent: list[dict] = []

    async def receive(self):
        return await self.receive_queue.get()

    async def send(self, ev):
        self.sent.append(ev)

    def disconnect(self) -> None:
        self.receive_queue.put_nowait({'type': 'http.disconnect'})

    def body_bytes(self) -> bytes:
        return b''.join(ev.get('body', b'') for ev in self.sent if ev['type'] == 'http.response.body')


def _parse_sse(body: bytes) -> list:
    out = []
    for chunk in body.decode('utf-8').split('\n\n'):
        if not chunk.strip():
            continue
        event = data = None
        for line in chunk.splitlines():
            if line.startswith('event: '):
                event = line[len('event: '):]
            elif line.startswith('data: '):
                data = json.loads(line[len('data: '):])
        out.append((event, data))
    return out


@pytest.mark.asyncs('asyncio')
async def test_web_timeline_sse_round_trip():
    script = mc.ChatScript([
        mc.ChatScriptTurn.of(
            mc.ThinkingMessage('mulling it over'),
            mc.AiMessage('a thoroughly web-served response'),
        ),
        mc.ChatScriptTurn.of(
            mc.AiMessage('and another one for good measure'),
        ),
    ])

    async with inj.create_async_managed_injector(bind_main(entrypoint_cfg=_chat_cfg(script))) as injector:
        app = await injector[ChatApp]
        driver = await injector[mc.drivers.Driver]
        manager = await injector[mc.facades.timelines.TimelineManager]

        await driver.start()
        try:
            # Attach the SSE client first - it sees everything live.
            sse = _AsgiCall('GET', '/timeline')
            sse_task = asyncio.create_task(app.handle(sse.scope, sse.receive, sse.send))

            # Two turns through the real input route.
            for text in ('hello web', 'again please'):
                post = _AsgiCall('POST', '/input', body=json.dumps({'text': text}).encode('utf-8'))
                await app.handle(post.scope, post.receive, post.send)
                resp = json.loads(post.body_bytes().decode('utf-8'))
                assert resp['ok']

            # A facade notice flows into the timeline too (the EventEmittingUiMessageDisplayer wiring).
            displayer = await injector[mc.facades.UiMessageDisplayer]
            await displayer.display_ui_message('a server-side notice')

            sse.disconnect()
            await sse_task

        finally:
            await driver.stop()

        # Reconstruct the conversation from the wire bytes alone.
        events = _parse_sse(sse.body_bytes())

        assert events[0][0] == 'window'
        head = events[0][1]
        window = msh.unmarshal(head['window'], mc.facades.timelines.TimelineWindow)

        proj = mc.facades.timelines.TimelineProjection()
        proj.initialize(window)

        for kind, data in events[1:]:
            assert kind == 'timeline'
            ev = msh.unmarshal(data, mc.Event)
            assert isinstance(ev, mc.facades.timelines.TimelineEvent)
            assert ev.watermark > head['watermark']
            proj.apply_event(ev)

        live = manager.state.get_items()
        assert canon_items(proj.items) == canon_items(live)

        # And the shapes are right: user echoes, thinking, prose, and the notice all made the trip.
        types = [type(it).__name__ for it in proj.items]
        assert types == [
            'UserMessageTimelineItem',
            'ThinkingTimelineItem',
            'AiMessageTimelineItem',
            'UserMessageTimelineItem',
            'AiMessageTimelineItem',
            'UiMessageTimelineItem',
        ]


@pytest.mark.asyncs('asyncio')
async def test_web_timeline_before_paging():
    script = mc.ChatScript([
        mc.ChatScriptTurn.of(mc.AiMessage(f'answer {i}'))
        for i in range(3)
    ])

    async with inj.create_async_managed_injector(bind_main(entrypoint_cfg=_chat_cfg(script))) as injector:
        app = await injector[ChatApp]
        driver = await injector[mc.drivers.Driver]

        await driver.start()
        try:
            for i in range(3):
                post = _AsgiCall('POST', '/input', body=json.dumps({'text': f'question {i}'}).encode('utf-8'))
                await app.handle(post.scope, post.receive, post.send)

            # A small attach window, then page back over the wire from its cursor.
            sse = _AsgiCall('GET', '/timeline', query_string=b'limit=2')
            sse_task = asyncio.create_task(app.handle(sse.scope, sse.receive, sse.send))
            sse.disconnect()
            await sse_task

        finally:
            await driver.stop()

        head = _parse_sse(sse.body_bytes())[0][1]
        window = msh.unmarshal(head['window'], mc.facades.timelines.TimelineWindow)
        assert window.has_before
        cursor = window.before_cursor
        assert cursor is not None

        before = _AsgiCall(
            'GET',
            '/timeline/before',
            query_string=f'item_id={cursor.item_id}&realm={cursor.realm}&key={cursor.key}&limit=10'.encode('ascii'),
        )
        await app.handle(before.scope, before.receive, before.send)

        before_window = msh.unmarshal(json.loads(before.body_bytes().decode('utf-8')), mc.facades.timelines.TimelineWindow)  # noqa

        proj = mc.facades.timelines.TimelineProjection()
        proj.initialize(window)
        proj.prepend_window(before_window)

        texts = [
            getattr(it.message, 'c', None) if hasattr(it, 'message') else None
            for it in proj.items
        ]
        assert texts == [
            'question 0', 'answer 0',
            'question 1', 'answer 1',
            'question 2', 'answer 2',
        ]
