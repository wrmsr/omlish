import asyncio
import contextlib
import subprocess
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.specs import jsonrpc as jr
from omlish.specs.jsonrpc import conns2 as jr2

from . import protocol as pt


##


class McpServerConnection:
    def __init__(
            self,
            stream: jr2.AsyncByteStream,
            *,
            default_timeout: float | None = 30.,
    ) -> None:
        super().__init__()

        self._conn = jr2.JsonrpcConnection(
            stream,
            request_handler=self._handle_client_request,
            notification_handler=self._handle_client_notification,
            default_timeout=default_timeout,
        )

    #

    @classmethod
    def from_process(
            cls,
            proc: asyncio.subprocess.Process,
            **kwargs: ta.Any,
    ) -> 'McpServerConnection':
        return cls(
            jr2.AsyncioStreamAdapter(
                check.not_none(proc.stdout),
                check.not_none(proc.stdin),
            ),
            **kwargs,
        )

    @classmethod
    def open_process(
            cls,
            cmd: ta.Sequence[str],
            open_kwargs: ta.Mapping[str, ta.Any] | None = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncContextManager[tuple[asyncio.subprocess.Process, 'McpServerConnection']]:
        @contextlib.asynccontextmanager
        async def inner() -> ta.AsyncIterator[tuple[asyncio.subprocess.Process, 'McpServerConnection']]:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                **(open_kwargs or {}),
            )

            try:
                async with cls.from_process(
                        proc,
                        **kwargs,
                ) as client:
                    yield (proc, client)

            finally:
                if proc.returncode is None:
                    if proc.stdin is not None:
                        proc.stdin.close()
                        with contextlib.suppress(Exception):
                            await proc.stdin.wait_closed()

                    proc.terminate()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=5)
                    except TimeoutError:
                        proc.kill()
                        with contextlib.suppress(Exception):
                            await proc.wait()
                else:
                    with contextlib.suppress(Exception):
                        await proc.wait()

        return inner()

    #

    async def __aenter__(self) -> ta.Self:
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, et, e, tb) -> None:
        await self._conn.__aexit__(et, e, tb)

    #

    async def _handle_client_request(self, _client: jr2.JsonrpcConnection, req: jr.Request) -> None:
        pass

    async def _handle_client_notification(self, _client: jr2.JsonrpcConnection, no: jr.Request) -> None:
        pass

    #

    async def request(self, req: pt.ClientRequest[pt.ClientResultT]) -> pt.ClientResultT:
        res_cls = pt.MESSAGE_TYPES_BY_JSON_RPC_METHOD_NAME[pt.ClientResult][req.json_rpc_method_name]  # type: ignore[type-abstract]  # noqa
        req_mv = msh.marshal(req)
        res_mv = await self._conn.request(req.json_rpc_method_name, req_mv)  # type: ignore[arg-type]
        res = msh.unmarshal(res_mv, res_cls)
        return ta.cast(pt.ClientResultT, res)

    async def notify(self, no: pt.Notification) -> None:
        no_mv = msh.marshal(no)
        await self._conn.notify(no.json_rpc_method_name, no_mv)  # type: ignore[arg-type]

    #

    async def yield_cursor_request(
            self,
            req: pt.CursorClientRequest[pt.CursorClientResultT],
    ) -> ta.AsyncGenerator[pt.CursorClientResultT]:
        check.none(req.cursor)

        cursor: str | None = None
        while True:
            res = await self.request(dc.replace(req, cursor=cursor))  # noqa
            yield res

            if (cursor := res.next_cursor) is None:
                break

    async def list_cursor_request(
            self,
            req: pt.CursorClientRequest[pt.CursorClientResultT],
    ) -> list[pt.CursorClientResultT]:
        return [res async for res in self.yield_cursor_request(req)]

    #

    async def list_tools(self) -> list[pt.Tool]:
        return [
            tool
            async for res in self.yield_cursor_request(pt.ListToolsRequest())
            for tool in res.tools
        ]

    async def list_prompts(self) -> list[pt.Prompt]:
        return [
            prompt
            async for res in self.yield_cursor_request(pt.ListPromptsRequest())
            for prompt in res.prompts
        ]
