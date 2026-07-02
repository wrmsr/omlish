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
from .interning import Interner
from .reflector import ForwardRefResolver
from .reflector import TypeReflector
from .reflector import UnresolvedForwardRefPolicy
from .typekeys import TypeKeys
from .universe import DynamicTypeNameSuffix
from .universe import TypeUniverse


if ta.TYPE_CHECKING:
    from .dataclasses import DataclassInspection
    from .dataclasses import DataclassInspector
    from .members import MembersInspection
    from .members import MembersInspector
    from .namedtuples import NamedtupleInspection
    from .namedtuples import NamedtupleInspector


T = ta.TypeVar('T')


##


@ta.final
class Api:
    def __init__(
            self,
            *,
            # universe
            dynamic_type_name_suffix: DynamicTypeNameSuffix | None = None,

            # reflector
            forward_ref_resolver: ForwardRefResolver | None = None,
            unresolved_forward_ref_policy: UnresolvedForwardRefPolicy | None = None,
    ) -> None:
        super().__init__()

        self._lock: ta.Final = threading.RLock()

        self._universe: ta.Final = TypeUniverse(
            dynamic_type_name_suffix=dynamic_type_name_suffix,
            lock=self._lock,
        )

        self._interner: ta.Final = Interner(
            lock=self._lock,
        )

        self._reflector: ta.Final = TypeReflector(
            forward_ref_resolver=forward_ref_resolver,
            unresolved_forward_ref_policy=unresolved_forward_ref_policy,
            universe=self._universe,
            interner=self._interner,
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

    def get_newtype_info(self, obj: object) -> TypeInfo:
        return self._universe.get_newtype_info(obj)

    def get_runtime_type(self, info: TypeInfo) -> object | None:
        return self._universe.get_runtime_type(info)

    #

    @property
    def interner(self) -> Interner:
        return self._interner

    def intern(self, obj: T) -> T:
        return self._interner.intern(obj)

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

    _members: MembersInspector

    def _members_(self) -> MembersInspector:
        with self._lock:
            try:
                return self._members
            except AttributeError:
                pass

        from .members import MembersInspector

        with self._lock:
            try:
                return self._members
            except AttributeError:
                pass

            self._members = MembersInspector(
                keys=self._keys,
                reflector=self._reflector,
                lock=self._lock,
            )

            return self._members

    @property
    def members(self) -> MembersInspector:
        try:
            return self._members
        except AttributeError:
            pass
        return self._members_()

    def inspect_members(self, obj: object) -> MembersInspection:
        return self.members.inspect_members(obj)

    #

    _dataclasses: DataclassInspector

    def _dataclasses_(self) -> DataclassInspector:
        with self._lock:
            try:
                return self._dataclasses
            except AttributeError:
                pass

        from .dataclasses import DataclassInspector

        with self._lock:
            try:
                return self._dataclasses
            except AttributeError:
                pass

            self._dataclasses = DataclassInspector(
                reflector=self._reflector,
                lock=self._lock,
            )

            return self._dataclasses

    @property
    def dataclasses(self) -> DataclassInspector:
        try:
            return self._dataclasses
        except AttributeError:
            pass
        return self._dataclasses_()

    def inspect_dataclass(self, obj: object) -> DataclassInspection:
        return self.dataclasses.inspect_dataclass(obj)

    #

    _namedtuples: NamedtupleInspector

    def _namedtuples_(self) -> NamedtupleInspector:
        with self._lock:
            try:
                return self._namedtuples
            except AttributeError:
                pass

        from .namedtuples import NamedtupleInspector

        with self._lock:
            try:
                return self._namedtuples
            except AttributeError:
                pass

            self._namedtuples = NamedtupleInspector(
                reflector=self._reflector,
                lock=self._lock,
            )

            return self._namedtuples

    @property
    def namedtuples(self) -> NamedtupleInspector:
        try:
            return self._namedtuples
        except AttributeError:
            pass
        return self._namedtuples_()

    def inspect_namedtuple(self, obj: object) -> NamedtupleInspection:
        return self.namedtuples.inspect_namedtuple(obj)


##


_GLOBAL_API: ta.Final = Api()


def global_api() -> Api:
    return _GLOBAL_API


def or_global_api(api: Api | None) -> Api:
    return _GLOBAL_API if api is None else api


##


def get_type_info(obj: type | str) -> TypeInfo:
    return _GLOBAL_API.get_type_info(obj)


def get_newtype_info(obj: object) -> TypeInfo:
    return _GLOBAL_API.get_newtype_info(obj)


def get_runtime_type(info: TypeInfo) -> object | None:
    return _GLOBAL_API.get_runtime_type(info)


#


def intern(obj: T) -> T:
    return _GLOBAL_API.intern(obj)


#


def reflect_type(obj: object) -> Type:
    return _GLOBAL_API.reflect_type(obj)


#


def type_key_or_none(
        typ: Type,
        policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
) -> TypeKey | None:
    return _GLOBAL_API.type_key_or_none(typ, policy)


def type_key(
        typ: Type,
        policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
) -> TypeKey:
    return _GLOBAL_API.type_key(typ, policy)


#


def to_runtime_annotation(
        typ: Type,
        *,
        type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
) -> object:
    return _GLOBAL_API.to_runtime_annotation(
        typ,
        type_alias_policy=type_alias_policy,
    )


#


def inspect_members(obj: object) -> MembersInspection:
    return _GLOBAL_API.inspect_members(obj)

#


def inspect_dataclass(obj: object) -> DataclassInspection:
    return _GLOBAL_API.inspect_dataclass(obj)

#


def inspect_namedtuple(obj: object) -> NamedtupleInspection:
    return _GLOBAL_API.inspect_namedtuple(obj)
