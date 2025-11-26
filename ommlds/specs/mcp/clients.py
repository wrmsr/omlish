import contextlib
import subprocess
import typing as ta

import anyio.abc

from omlish import check
from omlish import marshal as msh
from omlish.asyncs import anyio as aiu
from omlish.specs import jsonrpc as jr

from . import protocol as pt


ClientResultT = ta.TypeVar('ClientResultT', bound=pt.ClientResult)


##


class McpServerConnection:
    def __init__(
            self,
            tg: anyio.abc.TaskGroup,
            stream: anyio.abc.ByteStream,
            *,
            default_timeout: float | None = 30.,
    ) -> None:
        super().__init__()

        self._conn = jr.Connection(
            tg,
            stream,
            request_handler=self._handle_client_request,
            notification_handler=self._handle_client_notification,
            default_timeout=default_timeout,
        )

    #

    @classmethod
    def from_process(
            cls,
            tg: anyio.abc.TaskGroup,
            proc: anyio.abc.Process,
            **kwargs: ta.Any,
    ) -> 'McpServerConnection':
        return cls(
            tg,
            aiu.StapledByteStream(
                check.not_none(proc.stdin),
                check.not_none(proc.stdout),
            ),
            **kwargs,
        )

    @classmethod
    def open_process(
            cls,
            tg: anyio.abc.TaskGroup,
            cmd: ta.Sequence[str],
            open_kwargs: ta.Mapping[str, ta.Any] | None = None,
            **kwargs: ta.Any,
    ) -> ta.AsyncContextManager[tuple[anyio.abc.Process, 'McpServerConnection']]:
        @contextlib.asynccontextmanager
        async def inner():
            async with await anyio.open_process(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    **open_kwargs or {},
            ) as proc:
                async with cls.from_process(
                        tg,
                        proc,
                        **kwargs,
                ) as client:
                    yield (proc, client)

        return inner()

    #

    async def __aenter__(self) -> 'McpServerConnection':
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, et, e, tb) -> None:
        await self._conn.__aexit__(et, e, tb)

    #

    async def _handle_client_request(self, _client: jr.Connection, req: jr.Request) -> None:
        pass

    async def _handle_client_notification(self, _client: jr.Connection, no: jr.Request) -> None:
        pass

    #

    async def request(self, req: pt.ClientRequest, res_cls: type[ClientResultT]) -> ClientResultT:
        # res_cls = pt.MESSAGE_TYPES_BY_JSON_RPC_METHOD_NAME[pt.ClientResult][req.json_rpc_method_name]
        req_mv = msh.marshal(req)
        res_mv = await self._conn.request(req.json_rpc_method_name, req_mv)  # type: ignore[arg-type]
        res = msh.unmarshal(res_mv, res_cls)
        return res

    async def notify(self, no: pt.Notification) -> None:
        no_mv = msh.marshal(no)
        await self._conn.notify(no.json_rpc_method_name, no_mv)  # type: ignore[arg-type]
