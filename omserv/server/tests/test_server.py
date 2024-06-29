# import asyncio
#
# import h11
# import pytest
#
# from ..config import Config
# from ..tcpserver import TCPServer
# from ..types import ASGIWrapper
# from ..workercontext import WorkerContext
# from .asyncio_helpers import MemoryReader
# from .asyncio_helpers import MemoryWriter
# from .sanity import SANITY_BODY
# from .sanity import sanity_framework
#
#
# @pytest.mark.asyncio
# async def test_server_asyncio():
#     event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
#
#     server = TCPServer(
#         ASGIWrapper(sanity_framework),
#         event_loop,
#         Config(),
#         WorkerContext(None),
#         MemoryReader(),  # type: ignore
#         MemoryWriter(),  # type: ignore
#     )
#     task = event_loop.create_task(server.run())
#     client = h11.Connection(h11.CLIENT)
#     await server.reader.send(  # type: ignore
#         client.send(
#             h11.Request(
#                 method="POST",
#                 target="/",
#                 headers=[
#                     (b"host", b"hypercorn"),
#                     (b"connection", b"close"),
#                     (b"content-length", b"%d" % len(SANITY_BODY)),
#                 ],
#             )
#         )
#     )
#     await server.reader.send(client.send(h11.Data(data=SANITY_BODY)))  # type: ignore
#     await server.reader.send(client.send(h11.EndOfMessage()))  # type: ignore
#     events = []
#     while True:
#         event = client.next_event()
#         if event == h11.NEED_DATA:
#             data = await server.writer.receive()  # type: ignore
#             client.receive_data(data)
#         elif isinstance(event, h11.ConnectionClosed):
#             break
#         else:
#             events.append(event)
#
#     assert events == [
#         h11.Response(
#             status_code=200,
#             headers=[
#                 (b"content-length", b"15"),
#                 (b"date", b"Thu, 01 Jan 1970 01:23:20 GMT"),
#                 (b"server", b"hypercorn-h11"),
#                 (b"connection", b"close"),
#             ],
#             http_version=b"1.1",
#             reason=b"",
#         ),
#         h11.Data(data=b"Hello & Goodbye"),
#         h11.EndOfMessage(headers=[]),
#     ]
#     server.reader.close()  # type: ignore
#     await task
#
#
# @pytest.mark.trio
# async def test_server_trio():
#     pass
