import anyio
import pytest

from omlish.asyncs import anyio as aiu
from omlish.formats import json
from omlish import marshal as msh
from omlish.specs import jsonrpc as jr

from ..client import JsonrpcClient


@pytest.mark.asyncs('asyncio')
async def test_client():
    send_queue_tx, send_queue_rx = aiu.create_memory_object_stream()
    receive_queue_tx, receive_queue_rx = aiu.create_memory_object_stream()

    async with anyio.create_task_group() as tg:
        async with JsonrpcClient(
                tg,
                aiu.staple_memory_object_stream(
                    receive_queue_tx,
                    send_queue_rx,
                ),
        ) as client:
            msg = jr.notification('hi')
            mm = msh.marshal(msg)
            mj = json.dumps_compact(mm)
            mb = mj.encode('utf-8') + b'\n'
            await send_queue_tx.send(mb)
            await anyio.sleep(10.)
