import anyio
import pytest

from .... import marshal as msh
from ....asyncs import anyio as aiu
from ....formats import json
from ....specs import jsonrpc as jr
from ..conns import JsonrpcConnection


@pytest.mark.asyncs('asyncio')
async def test_conns():
    async def request_handler(conn: JsonrpcConnection, req: jr.Request) -> None:
        await conn.send_message(jr.result(jr.check_not_not_specified(req.id), 'hello'))  # type: ignore

    #

    send_queue_tx, send_queue_rx = aiu.create_memory_object_stream()  # type: ignore
    receive_queue_tx, receive_queue_rx = aiu.create_memory_object_stream()  # type: ignore

    async with anyio.create_task_group() as tg:
        async with JsonrpcConnection(
                tg,
                aiu.staple_memory_object_stream(  # type: ignore
                    receive_queue_tx,  # type: ignore
                    send_queue_rx,  # type: ignore
                ),
                request_handler=request_handler,
        ) as client:  # noqa
            try:
                msg = jr.request(1, 'hi')
                mm = msh.marshal(msg)
                mj = json.dumps_compact(mm)
                mb = mj.encode('utf-8') + b'\n'

                await send_queue_tx.send(mb)

                resp_buf = await receive_queue_rx.receive()
                resp_dct = json.loads(resp_buf.decode('utf-8'))
                resp: jr.Response = msh.unmarshal(resp_dct, jr.detect_message_type(resp_dct))  # type: ignore
                assert resp.is_result
                assert resp.result == 'hello'

            finally:
                send_queue_tx.close()
                receive_queue_tx.close()
