import json
import struct
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import ObjMarshalerManager


class Channel:
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

    def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        self._output.flush()

    def recv_obj(self, ty: ta.Any) -> ta.Any:
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
