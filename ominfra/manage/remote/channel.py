# ruff: noqa: UP006 UP007
import asyncio
import json
import struct
import sys
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import ObjMarshalerManager


T = ta.TypeVar('T')


class RemoteChannel:
    def __init__(
            self,
            input: asyncio.StreamReader,  # noqa
            output: asyncio.StreamWriter,
            *,
            msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
    ) -> None:
        super().__init__()

        self._input = input
        self._output = output
        self._msh = msh

        self._lock = asyncio.Lock()

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:
        self._msh = msh

    #

    async def _send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        sys.stderr.write('_send_obj\n')
        sys.stderr.write(repr(d) + '\n')
        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        await self._output.drain()
        sys.stderr.write('-_send_obj\n')

    async def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        async with self._lock:
            return await self._send_obj(o, ty)

    #

    async def _recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        sys.stderr.write('_recv_obj\n')
        d = await self._input.read(4)
        sys.stderr.write(repr(d) + '\n')
        if not d:
            return None
        if len(d) != 4:
            raise EOFError

        sz = struct.unpack('<I', d)[0]
        sys.stderr.write(repr(sz) + '\n')
        d = await self._input.read(sz)
        sys.stderr.write(repr(d) + '\n')
        if len(d) != sz:
            raise EOFError

        j = json.loads(d.decode('utf-8'))
        sys.stderr.write(repr(j) + '\n')
        return self._msh.unmarshal_obj(j, ty)

    async def recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        async with self._lock:
            return await self._recv_obj(ty)
