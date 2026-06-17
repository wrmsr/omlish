# ruff: noqa: SLF001
import typing as ta

from .core.typekeys import TYPE_KEY
from .core.typekeys import StandardTypeKeyPolicy
from .core.typekeys import TypeKey
from .core.typekeys import TypeKeyPolicy
from .core.typekeys import get_type_key_policy
from .core.typekeys import make_type_key_not_implemented_exception
from .core.typekeys import type_key_or_none
from .core.types import Type
from .locking import HasLock


ForwardRefResolver: ta.TypeAlias = ta.Callable[[str], object]


##


@ta.final
class TypeKeys(HasLock):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._type_key_cache: dict[tuple[TypeKeyPolicy, Type], TypeKey | None] = {}

    #

    def _type_key_or_none(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey | None:
        tk_policy = get_type_key_policy(policy)
        cache_key = (tk_policy, typ)
        try:
            return self._type_key_cache[cache_key]
        except KeyError:
            pass

        key = type_key_or_none(typ, tk_policy)
        self._type_key_cache[cache_key] = key
        return key

    def type_key_or_none(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey | None:
        tk_policy = get_type_key_policy(policy)
        cache_key = (tk_policy, typ)
        try:
            return self._type_key_cache[cache_key]
        except KeyError:
            pass

        with self._lock:
            return self._type_key_or_none(typ, tk_policy)

    def type_key(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey:
        key = self.type_key_or_none(typ, policy)
        if key is None:
            raise make_type_key_not_implemented_exception(typ, policy)
        return key


##


class HasKeys:
    def __init__(
            self,
            *,
            keys: TypeKeys,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._keys = keys
