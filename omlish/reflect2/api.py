import threading
import typing as ta

from .core.symbols import TypeInfo
from .core.typekeys import TYPE_KEY
from .core.typekeys import StandardTypeKeyPolicy
from .core.typekeys import TypeKey
from .core.typekeys import TypeKeyPolicy
from .core.types import Type
from .interning import Interner
from .needs import NeedsInterner
from .needs import NeedsKeys
from .needs import NeedsLock
from .needs import NeedsReflector
from .needs import NeedsUniverse
from .reflector import ForwardRefResolver
from .reflector import TypeReflector
from .reflector import UnresolvedForwardRefPolicy
from .universe import DynamicTypeNameSuffix
from .universe import TypeUniverse


if ta.TYPE_CHECKING:
    from .annotations import TypeAliasAnnotationPolicy
    from .annotations import TypeAnnotations
    from .dataclasses import DataclassInspection
    from .dataclasses import DataclassInspector
    from .members import MembersInspection
    from .members import MembersInspector
    from .namedtuples import NamedtupleInspection
    from .namedtuples import NamedtupleInspector
    from .typekeys import TypeKeys


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

        self._interner: ta.Final = self._inject(Interner)

        self._universe: ta.Final = self._inject(
            TypeUniverse,
            dynamic_type_name_suffix=dynamic_type_name_suffix,
        )

        self._reflector: ta.Final = self._inject(
            TypeReflector,
            forward_ref_resolver=forward_ref_resolver,
            unresolved_forward_ref_policy=unresolved_forward_ref_policy,
        )

    #

    def _inject(self, cls: type[T], **kwargs: ta.Any) -> T:
        nkw: dict[str, ta.Any] = {}

        if issubclass(cls, NeedsLock):
            nkw['lock'] = self._lock

        if issubclass(cls, NeedsInterner):
            nkw['interner'] = self._interner

        if issubclass(cls, NeedsUniverse):
            nkw['universe'] = self.universe

        if issubclass(cls, NeedsReflector):
            nkw['reflector'] = self.reflector

        if issubclass(cls, NeedsKeys):
            nkw['keys'] = self.keys

        return cls(**kwargs, **nkw)

    def _init_injected(self, cls: type[T], attr: str) -> T:
        with self._lock:
            try:
                return getattr(self, attr)
            except AttributeError:
                pass

        with self._lock:
            try:
                return getattr(self, attr)
            except AttributeError:
                pass

            inst = self._inject(cls)
            setattr(self, attr, inst)
            return inst

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
    def reflector(self) -> TypeReflector:
        return self._reflector

    def reflect_type(self, obj: object) -> Type:
        return self._reflector.reflect_type(obj)

    #

    _keys: TypeKeys

    @property
    def keys(self) -> TypeKeys:
        try:
            return self._keys
        except AttributeError:
            pass

        from .typekeys import TypeKeys
        return self._init_injected(TypeKeys, '_keys')

    def type_key_or_none(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey | None:
        return self.keys.type_key_or_none(typ, policy)

    def type_key(
            self,
            typ: Type,
            policy: TypeKeyPolicy | StandardTypeKeyPolicy = TYPE_KEY,
    ) -> TypeKey:
        return self.keys.type_key(typ, policy)

    #

    _annotations: TypeAnnotations

    @property
    def annotations(self) -> TypeAnnotations:
        try:
            return self._annotations
        except AttributeError:
            pass

        from .annotations import TypeAnnotations
        return self._init_injected(TypeAnnotations, '_annotations')

    def to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        return self.annotations.to_runtime_annotation(
            typ,
            type_alias_policy=type_alias_policy,
        )

    #

    _members: MembersInspector

    @property
    def members(self) -> MembersInspector:
        try:
            return self._members
        except AttributeError:
            pass

        from .members import MembersInspector
        return self._init_injected(MembersInspector, '_members')

    def inspect_members(self, obj: object) -> MembersInspection:
        return self.members.inspect_members(obj)

    #

    _dataclasses: DataclassInspector

    @property
    def dataclasses(self) -> DataclassInspector:
        try:
            return self._dataclasses
        except AttributeError:
            pass

        from .dataclasses import DataclassInspector
        return self._init_injected(DataclassInspector, '_dataclasses')

    def inspect_dataclass(self, obj: object) -> DataclassInspection:
        return self.dataclasses.inspect_dataclass(obj)

    #

    _namedtuples: NamedtupleInspector

    @property
    def namedtuples(self) -> NamedtupleInspector:
        try:
            return self._namedtuples
        except AttributeError:
            pass

        from .namedtuples import NamedtupleInspector
        return self._init_injected(NamedtupleInspector, '_namedtuples')

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
