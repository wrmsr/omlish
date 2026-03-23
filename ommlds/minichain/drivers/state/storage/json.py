import os.path
import typing as ta

from omlish.formats import json

from .marshaled import MarshaledStateStorage


T = ta.TypeVar('T')


##


class JsonFileStateStorage(MarshaledStateStorage):
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
        data = json.dumps_compact(data)
        with open(self._file, 'w') as f:
            f.write(data)

    #

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        if not (data := self._load_file_data()):
            return None
        if (dct := data.get(key)) is None:
            return None
        return self._unmarshal_state(dct, ty)

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        if (data := self._load_file_data()) is None:
            data = {}
        if obj is None:
            data.pop(key, None)
        else:
            dct = self._marshal_state(obj, ty)
            data[key] = dct
        self._save_file_data(data)
