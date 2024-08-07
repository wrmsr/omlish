import dataclasses as dc
import functools

import anyio.abc
import anyio.streams.stapled

from omlish.asyncs import anyio as aiu

from ..types import Context
from ..types import Service


@dc.dataclass()
class Incrementor(Service):
    current: int
    next: anyio.abc.ObjectStream[int]
    stop: anyio.abc.ObjectStream[bool]

    async def serve(self, ctx: Context) -> Exception | None:
        while True:
            next_m, done_m = aiu.gather(functools.partial(self.next.send, self.current), ctx.done)
            if next_m.present:
                self.current += 1
            if done_m.present:
                # This message on i.stop is just to synchronize this test with the example code so the output is
                # consistent for the test code; most services would just "return nil" here.
                print("Stopping the service")
                await self.stop.send(True)
                return None


async def main():
    supervisor = NewSimpleSupervisor("Supervisor")

    service = Incrementor(
        0,
        aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[int]()),
        aiu.staple_memory_object_stream(*anyio.create_memory_object_stream[bool]()),
    )

    supervisor.add(service)

    ctx, cancel = context.WithCancel(context.Background())
    supervisor.ServeBackground(ctx)

    print("Got:", await service.next.receive())
    print("Got:", await service.next.receive())
    cancel()

    # We sync here just to guarantee the output of "Stopping the service"
    await service.stop.receive()
