import typing as ta

from ... import cached
from ... import dataclasses as dc
from ..binder import bind
from ..elements import Elemental
from ..elements import as_elements
from ..keys import Key
from ..keys import as_key
from ..privates import private


##


@ta.final
class WrapperBinderHelper:
    def __init__(
            self,
            key: ta.Any,
            *,
            unwrapped_key: ta.Any | None = None,
    ) -> None:
        self._key = as_key(key)
        self._unwrapped_key = unwrapped_key

        self._root = WrapperBinderHelper._Root()
        self._top = WrapperBinderHelper._Level(self._root, 0)

    @dc.dataclass(frozen=True, eq=False)
    @dc.extra_class_params(repr_id=True)
    class _Root:
        pass

    @dc.dataclass(frozen=True)
    class _Level:
        root: 'WrapperBinderHelper._Root'
        level: int

        def next(self) -> 'WrapperBinderHelper._Level':
            return WrapperBinderHelper._Level(self.root, self.level + 1)

        @cached.property
        def key(self) -> Key:
            return Key(ta.Any, tag=self)

    @property
    def top(self) -> Key:
        return self._top.key

    def push_bind(self, with_: ta.Sequence[Elemental] | None = None, **kwargs: ta.Any) -> Elemental:
        prv = self._top
        nxt = prv.next()
        out = private(
            *([
                bind(sk := self._key, to_key=prv.key),
                *([bind(suk, to_key=sk)] if (suk := self._unwrapped_key) is not None else []),
            ] if prv.level else []),
            bind(nxt.key, **kwargs, expose=True),
            *([as_elements(*with_)] if with_ is not None else []),
        )
        self._top = nxt
        return out


wrapper_binder_helper = WrapperBinderHelper
