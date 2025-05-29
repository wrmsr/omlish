import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish import lang
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


class StateStorage(lang.Abstract):
    def __init__(
            self,
            *,
            version: int = STATE_VERSION,
    ) -> None:
        super().__init__()

        self._version = version

    #

    def unmarshal_state(self, obj: ta.Any, ty: type[T] | None = None) -> T | None:
        ms = msh.unmarshal(obj, MarshaledState)
        if ms.version < self._version:
            return None
        return msh.unmarshal(ms.payload, ty)  # type: ignore

    def marshal_state(self, obj: ta.Any, ty: type | None = None) -> ta.Any:
        ms = MarshaledState(
            version=self._version,
            payload=msh.marshal(obj, ty),
        )
        return msh.marshal(ms)

    #

    @abc.abstractmethod
    def load_state(self, key: str, ty: type[T] | None) -> T | None:
        raise NotImplementedError

    @abc.abstractmethod
    def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        raise NotImplementedError


#


class JsonFileStateStorage(StateStorage):
    def __init__(
            self,
            file: str,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._file = file

    #

    def _load_file_data(self) -> ta.Any | None:
        if not os.path.isfile(self._file):
            return None
        with open(self._file) as f:
            data = f.read()
        return json.loads(data)

    def _save_file_data(self, data: ta.Any) -> None:
        data = json.dumps_pretty(data)
        with open(self._file, 'w') as f:
            f.write(data)

    #

    def load_state(self, key: str, ty: type[T] | None) -> T | None:
        if not (data := self._load_file_data()):
            return None
        if (dct := data.get(key)) is None:
            return None
        return self.unmarshal_state(dct, ty)

    def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        if (data := self._load_file_data()) is None:
            data = {}
        if obj is None:
            data.pop(key, None)
        else:
            dct = self.marshal_state(obj, ty)
            data[key] = dct
        self._save_file_data(data)
