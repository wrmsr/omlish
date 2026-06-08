"""
The timeline-over-the-wire handlers: the proof that a remote frontend is 'attach, serialize the window, stream the
events' - zero translation beyond the marshal system.

- GET /timeline -> SSE: one `window` event carrying the marshaled attach window + watermark, then a `timeline` event
  per marshaled TimelineEvent, until the client disconnects.
- GET /timeline/before?item_id=&realm=&key=&limit= -> one marshaled window (lazy scrollback over the wire; the cursor
  fields round-trip a marshaled TimelineCursor).

A browser holding a `TimelineProjection`-equivalent (apply window, apply events, upsert by id) renders this exactly as
the TUI does - which is what the tests assert, projection included.
"""
import asyncio
import typing as ta

from omlish import marshal as msh

from ..... import minichain as mc
from .helpers import parse_query
from .helpers import send_json
from .helpers import send_sse_headers
from .helpers import sse_bytes


##


class TimelineSseHandler:
    """One driver's timeline, attachable by any number of concurrent web clients."""

    DEFAULT_ATTACH_LIMIT: ta.ClassVar[int] = 200

    def __init__(
            self,
            *,
            timeline: mc.facades.timelines.Timeline,
    ) -> None:
        super().__init__()

        self._timeline = timeline

    async def handle_attach(self, scope: ta.Any, receive: ta.Any, send: ta.Any) -> None:
        qs = parse_query(scope)
        limit = int(qs.get('limit', self.DEFAULT_ATTACH_LIMIT))

        att = await self._timeline.attach(limit)

        async with att:
            await send_sse_headers(send)

            await send({
                'type': 'http.response.body',
                'body': sse_bytes('window', {
                    'timeline_id': str(self._timeline.timeline_id),
                    'watermark': att.watermark,
                    'window': msh.marshal(att.window, mc.facades.timelines.TimelineWindow),
                }),
                'more_body': True,
            })

            recv_task = asyncio.create_task(receive())
            get_task: asyncio.Task | None = None

            try:
                while True:
                    if get_task is None:
                        get_task = asyncio.create_task(att.subscription.get())

                    done, _ = await asyncio.wait(
                        [recv_task, get_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # Ready events flush before disconnects are honored - a closing client still receives everything
                    # already buffered for it.
                    if get_task in done:
                        try:
                            tl_ev = get_task.result()
                        except mc.facades.timelines.TimelineSubscriptionClosedError:
                            break
                        finally:
                            get_task = None

                        await send({
                            'type': 'http.response.body',
                            'body': sse_bytes('timeline', msh.marshal(tl_ev, mc.Event)),
                            'more_body': True,
                        })

                        continue

                    if recv_task in done:
                        ev = recv_task.result()
                        if ev['type'] == 'http.disconnect':
                            break

                        recv_task = asyncio.create_task(receive())

            finally:
                for t in (recv_task, get_task):
                    if t is not None and not t.done():
                        t.cancel()

            await send({
                'type': 'http.response.body',
                'body': b'',
                'more_body': False,
            })

    async def handle_before(self, scope: ta.Any, receive: ta.Any, send: ta.Any) -> None:
        qs = parse_query(scope)

        cursor = msh.unmarshal(
            {
                'item_id': qs['item_id'],
                'realm': qs['realm'],
                'key': int(qs['key']),
            },
            mc.facades.timelines.TimelineCursor,
        )

        window = await self._timeline.get_before(cursor, int(qs.get('limit', '50')))

        await send_json(send, msh.marshal(window, mc.facades.timelines.TimelineWindow))
