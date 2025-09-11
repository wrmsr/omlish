import typing as ta

from .lexing import SCALAR_VALUE_TYPES
from .parsing import BeginArray
from .parsing import BeginObject
from .parsing import EndArray
from .parsing import EndObject
from .parsing import Event
from .parsing import JsonStreamObject
from .parsing import Key


##


class JsonValueBuilder:
    def __init__(
            self,
            *,
            yield_object_lists: bool = False,
    ) -> None:
        super().__init__()

        self._stack: list[JsonStreamObject | list | Key] = []
        self._yield_object_lists = yield_object_lists

    class StateError(Exception):
        pass

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.close()

    def close(self) -> None:
        if self._stack:
            raise self.StateError

    def _emit_value(self, v: ta.Any) -> ta.Iterable[ta.Any]:
        if not (stk := self._stack):
            return (v,)

        tv = stk[-1]
        if isinstance(tv, Key):
            stk.pop()
            if not stk:
                raise self.StateError

            tv2 = stk[-1]
            if not isinstance(tv2, JsonStreamObject):
                raise self.StateError

            tv2.append((tv.key, v))
            return ()

        elif isinstance(tv, list):
            tv.append(v)
            return ()

        else:
            raise self.StateError

    def __call__(self, e: Event) -> ta.Iterable[ta.Any]:
        stk = self._stack

        #

        if isinstance(e, SCALAR_VALUE_TYPES):
            return self._emit_value(e)

        #

        elif e is BeginObject:
            stk.append(JsonStreamObject())
            return ()

        elif isinstance(e, Key):
            if not stk or not isinstance(stk[-1], JsonStreamObject):
                raise self.StateError

            stk.append(e)
            return ()

        elif e is EndObject:
            tv: ta.Any
            if not stk or not isinstance(tv := stk.pop(), JsonStreamObject):
                raise self.StateError

            if not self._yield_object_lists:
                tv = dict(tv)

            return self._emit_value(tv)

        #

        elif e is BeginArray:
            stk.append([])
            return ()

        elif e is EndArray:
            if not stk or not isinstance(tv := stk.pop(), list):
                raise self.StateError

            return self._emit_value(tv)

        #

        else:
            raise TypeError(e)
