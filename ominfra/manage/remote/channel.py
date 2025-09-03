# ruff: noqa: UP006 UP007 UP045
import abc
import asyncio
import json
import struct
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import ObjMarshalerManager


T = ta.TypeVar('T')


##


class RemoteChannel(Abstract):
    @abc.abstractmethod
    def send_obj(self, o: ta.Any, ty: ta.Any = None) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def recv_obj(self, ty: ta.Type[T]) -> ta.Awaitable[ta.Optional[T]]:
        raise NotImplementedError

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:  # noqa
        pass


##


class RemoteChannelImpl(RemoteChannel):
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

        self._input_lock = asyncio.Lock()
        self._output_lock = asyncio.Lock()

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:
        self._msh = msh

    #

    async def _send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        await self._output.drain()

    async def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        async with self._output_lock:
            return await self._send_obj(o, ty)

    #

    async def _recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        d = await self._input.read(4)
        if not d:
            return None
        if len(d) != 4:
            raise EOFError

        sz = struct.unpack('<I', d)[0]
        d = await self._input.read(sz)
        if len(d) != sz:
            raise EOFError

        j = json.loads(d.decode('utf-8'))
        return self._msh.unmarshal_obj(j, ty)

    async def recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        async with self._input_lock:
            return await self._recv_obj(ty)
