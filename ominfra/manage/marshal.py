import dataclasses as dc
import typing as ta

from omcore.lite.marshal import ObjMarshalerManager


##


@dc.dataclass(frozen=True)
class ObjMarshalerInstaller:
    fn: ta.Callable[[ObjMarshalerManager], None]


ObjMarshalerInstallers = ta.NewType('ObjMarshalerInstallers', ta.Sequence[ObjMarshalerInstaller])
