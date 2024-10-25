import typing as ta

from ....genmachine import GenMachine
from .lex import SCALAR_VALUE_TYPES
from .parse import BeginArray
from .parse import BeginObject
from .parse import EndArray
from .parse import EndObject
from .parse import JsonStreamObject
from .parse import JsonStreamParserEvent
from .parse import Key


##


class JsonObjectBuilder(GenMachine[JsonStreamParserEvent, ta.Any]):
    def __init__(
            self,
            *,
            yield_object_lists: bool = False,
    ) -> None:
        self._stack: list[JsonStreamObject | list | Key] = []
        self._yield_object_lists = yield_object_lists

        super().__init__(self._do())

    def _do(self):
        stk = self._stack

        def emit_value(v):
            if not stk:
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

        while True:
            try:
                e = yield None
            except GeneratorExit:
                if stk:
                    raise self.StateError from None
                else:
                    raise

            #

            if isinstance(e, SCALAR_VALUE_TYPES):
                if t := emit_value(e):
                    yield t
                continue

            #

            elif e is BeginObject:
                stk.append(JsonStreamObject())
                continue

            elif isinstance(e, Key):
                if not stk or not isinstance(stk[-1], JsonStreamObject):
                    raise self.StateError

                stk.append(e)
                continue

            elif e is EndObject:
                tv: ta.Any
                if not stk or not isinstance(tv := stk.pop(), JsonStreamObject):
                    raise self.StateError

                if not self._yield_object_lists:
                    tv = dict(tv)

                if t := emit_value(tv):
                    yield t
                continue

            #

            elif e is BeginArray:
                stk.append([])
                continue

            elif e is EndArray:
                if not stk or not isinstance(tv := stk.pop(), list):
                    raise self.StateError

                if t := emit_value(tv):
                    yield t
                continue

            #

            else:
                raise TypeError(e)
