import typing as ta

import anyio.abc
import anyio.streams.stapled

from .types import Node
from .types import Pid
from .impl import NodeImpl
from .actors import Actor
from .actors import ActorBehavior


class FooActor(Actor, ActorBehavior):
    async def handle_message(self, src: Pid, msg: ta.Any) -> None:
        print(f'{self} <- {msg}')


async def _main() -> None:
    async with anyio.create_task_group() as tg:
        node: Node = NodeImpl(tg)
        pid = await node.spawn(FooActor)
        print(pid)
        await node.send(pid, 'foo')


if __name__ == '__main__':
    anyio.run(_main)
