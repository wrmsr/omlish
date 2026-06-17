import threading
import typing as ta

from .annotations import TypeAliasAnnotationPolicy
from .annotations import TypeAnnotations
from .core.symbols import TypeInfo
from .core.typekeys import TYPE_KEY
from .core.typekeys import StandardTypeKeyPolicy
from .core.typekeys import TypeKey
from .core.typekeys import TypeKeyPolicy
from .core.types import Type
from .reflector import ForwardRefResolver
from .reflector import TypeReflector
from .typekeys import TypeKeys
from .universe import TypeUniverse
from .universe import or_global_universe


if ta.TYPE_CHECKING:
    from .members import MembersInspection
    from .members import MembersReflector


##


@ta.final
class Api:
    def __init__(
            self,
            universe: TypeUniverse | None = None,
            *,
            forward_ref_resolver: ForwardRefResolver | None = None,
    ) -> None:
        super().__init__()

        self._universe: ta.Final = or_global_universe(universe)

        self._lock: ta.Final = threading.RLock()

        self._reflector: ta.Final = TypeReflector(
            forward_ref_resolver=forward_ref_resolver,
            universe=self._universe,
            lock=self._lock,
        )

        self._keys: ta.Final = TypeKeys(
            lock=self._lock,
        )

        self._annotations: ta.Final = TypeAnnotations(
            reflector=self._reflector,
            lock=self._lock,
        )

    #

    @property
    def universe(self) -> TypeUniverse:
        return self._universe

    def get_type_info(self, obj: type | str) -> TypeInfo:
        return self._universe.get_type_info(obj)

    #

    @property
    def reflector(self) -> TypeReflector:
        return self._reflector

    def reflect_type(self, obj: object) -> Type:
        return self._reflector.reflect_type(obj)

    #

    @property
    def keys(self) -> TypeKeys:
        return self._keys

    def type_key_or_none(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey | None:
        return self._keys.type_key_or_none(typ, policy)

    def type_key(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey:
        return self._keys.type_key(typ, policy)

    #

    @property
    def annotations(self) -> TypeAnnotations:
        return self._annotations

    def to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        return self._annotations.to_runtime_annotation(
            typ,
            type_alias_policy=type_alias_policy,
        )

    #

    _members: MembersReflector

    def _members_(self) -> MembersReflector:
        with self._lock:
            try:
                return self._members
            except AttributeError:
                pass

        from .members import MembersReflector

        with self._lock:
            try:
                return self._members
            except AttributeError:
                pass

            self._members = MembersReflector(
                keys=self._keys,
                reflector=self._reflector,
                lock=self._lock,
            )

            return self._members

    @property
    def members(self) -> MembersReflector:
        try:
            return self._members
        except AttributeError:
            pass
        return self._members_()

    def inspect_members(self, obj: object) -> MembersInspection:
        return self.members.inspect_members(obj)


##


_GLOBAL_API: ta.Final = Api()


def global_api() -> Api:
    return _GLOBAL_API


def or_global_api(api: Api | None) -> Api:
    return _GLOBAL_API if api is None else api
