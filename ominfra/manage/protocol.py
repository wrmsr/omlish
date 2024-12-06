import json
import struct
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj


def send_obj(f: ta.IO, o: ta.Any, ty: ta.Any = None) -> None:
    j = json_dumps_compact(marshal_obj(o, ty))
    d = j.encode('utf-8')

    f.write(struct.pack('<I', len(d)))
    f.write(d)
    f.flush()


def recv_obj(f: ta.IO, ty: ta.Any) -> ta.Any:
    d = f.read(4)
    if not d:
        return None
    if len(d) != 4:
        raise EOFError

    sz = struct.unpack('<I', d)[0]
    d = f.read(sz)
    if len(d) != sz:
        raise EOFError

    j = json.loads(d.decode('utf-8'))
    return unmarshal_obj(j, ty)
