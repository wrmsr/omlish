import dataclasses as dc
import os.path
import typing as ta

from omlish import marshal as msh
from omlish.formats import json


T = ta.TypeVar('T')


##


STATE_VERSION = 0


@dc.dataclass(frozen=True)
class MarshaledState:
    version: int
    payload: ta.Any


#


def marshal_state(obj: ta.Any, ty: type | None = None, *, version: int = STATE_VERSION) -> ta.Any:
    ms = MarshaledState(
        version=version,
        payload=msh.marshal(obj, ty),
    )
    return msh.marshal(ms)


def save_state(file: str, obj: ta.Any, ty: type[T] | None, *, version: int = STATE_VERSION) -> bool:
    dct = marshal_state(obj, ty, version=version)
    data = json.dumps_pretty(dct)
    with open(file, 'w') as f:
        f.write(data)
    return True


#


def unmarshal_state(obj: ta.Any, ty: type[T] | None = None, *, version: int = STATE_VERSION) -> T | None:
    ms = msh.unmarshal(obj, MarshaledState)
    if ms.version < version:
        return None
    return msh.unmarshal(ms.payload, ty)  # type: ignore


def load_state(file: str, ty: type[T] | None, *, version: int = STATE_VERSION) -> T | None:
    if not os.path.isfile(file):
        return None
    with open(file) as f:
        data = f.read()
    dct = json.loads(data)
    return unmarshal_state(dct, ty, version=version)
