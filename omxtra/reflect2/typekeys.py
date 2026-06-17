# ruff: noqa: SLF001
import typing as ta

from .core.typekeys import ALPHA_STRUCTURAL_TYPE_KEY
from .core.typekeys import ALPHA_TYPE_KEY
from .core.typekeys import STRUCTURAL_TYPE_KEY
from .core.typekeys import TYPE_KEY
from .core.typekeys import TypeKey
from .core.typekeys import TypeKeyPolicy
from .core.typekeys import make_type_key_not_implemented_exception
from .core.typekeys import type_key_or_none
from .core.types import Type
from .locking import HasLock


ForwardRefResolver: ta.TypeAlias = ta.Callable[[str], object]


##


class TypeKeys(HasLock):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._type_key_cache: dict[tuple[TypeKeyPolicy, Type], TypeKey | None] = {}

    #

    def _type_key_or_none(self, typ: Type, policy: TypeKeyPolicy = TYPE_KEY) -> TypeKey | None:
        cache_key = (policy, typ)
        try:
            return self._type_key_cache[cache_key]
        except KeyError:
            pass

        key = type_key_or_none(typ, policy)
        self._type_key_cache[cache_key] = key
        return key

    def type_key_or_none(self, typ: Type, policy: TypeKeyPolicy = TYPE_KEY) -> TypeKey | None:
        cache_key = (policy, typ)
        try:
            return self._type_key_cache[cache_key]
        except KeyError:
            pass

        with self._lock:
            return self._type_key_or_none(typ, policy)

    def type_key(self, typ: Type, policy: TypeKeyPolicy = TYPE_KEY) -> TypeKey:
        key = self.type_key_or_none(typ, policy)
        if key is None:
            raise make_type_key_not_implemented_exception(typ, policy)
        return key

    def alpha_type_key_or_none(self, typ: Type) -> TypeKey | None:
        return self.type_key_or_none(typ, ALPHA_TYPE_KEY)

    def alpha_type_key(self, typ: Type) -> TypeKey:
        return self.type_key(typ, ALPHA_TYPE_KEY)

    def structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        return self.type_key_or_none(typ, STRUCTURAL_TYPE_KEY)

    def structural_type_key(self, typ: Type) -> TypeKey:
        return self.type_key(typ, STRUCTURAL_TYPE_KEY)

    def alpha_structural_type_key_or_none(self, typ: Type) -> TypeKey | None:
        return self.type_key_or_none(typ, ALPHA_STRUCTURAL_TYPE_KEY)

    def alpha_structural_type_key(self, typ: Type) -> TypeKey:
        return self.type_key(typ, ALPHA_STRUCTURAL_TYPE_KEY)
