# ruff: noqa: UP006 UP007
import json
import struct
import threading
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import ObjMarshalerManager


T = ta.TypeVar('T')


class RemoteChannel:
    def __init__(
            self,
            input: ta.IO,  # noqa
            output: ta.IO,
            *,
            msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
    ) -> None:
        super().__init__()

        self._input = input
        self._output = output
        self._msh = msh

        self._lock = threading.RLock()

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:
        self._msh = msh

    def _send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        self._output.flush()

    def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        with self._lock:
            return self._send_obj(o, ty)

    def _recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        d = self._input.read(4)
        if not d:
            return None
        if len(d) != 4:
            raise EOFError

        sz = struct.unpack('<I', d)[0]
        d = self._input.read(sz)
        if len(d) != sz:
            raise EOFError

        j = json.loads(d.decode('utf-8'))
        return self._msh.unmarshal_obj(j, ty)

    def recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        with self._lock:
            return self._recv_obj(ty)
