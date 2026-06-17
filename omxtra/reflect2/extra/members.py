# ruff: noqa: SLF001
import dataclasses as dc
import enum
import inspect
import types as pytypes
import typing as ta

from ..core.substitute import SubstitutionMap
from ..core.substitute import substitute_type
from ..core.subtypes import MroEntry
from ..core.subtypes import get_mro_entries
from ..core.typekeys import TypeKey
from ..core.typeops import get_type_alias_target
from ..core.types import _ANY_TYPES
from ..core.types import AnnotatedType
from ..core.types import AnyType
from ..core.types import Instance
from ..core.types import Type
from ..core.types import TypeAliasType
from ..core.types import TypeOfAny
from ..errors import ReflectionTypeError
from ..errors import UnreflectableTypeError
from ..locking import HasLock
from ..reflector import HasReflector
from ..typekeys import HasKeys


##


class RuntimeMemberKind(enum.Enum):
    FUNCTION = 'function'
    STATICMETHOD = 'staticmethod'
    CLASSMETHOD = 'classmethod'
    PROPERTY = 'property'
    DATA = 'data'


@dc.dataclass(frozen=True)
class RuntimeMemberParameter:
    name: str
    kind: inspect._ParameterKind
    typ: Type
    has_default: bool


@dc.dataclass(frozen=True)
class RuntimeMemberSignature:
    parameters: tuple[RuntimeMemberParameter, ...]
    return_type: Type


@dc.dataclass(frozen=True)
class RuntimeMember:
    name: str
    kind: RuntimeMemberKind
    owner: type
    obj: object
    signature: inspect.Signature | None
    reflected_signature: RuntimeMemberSignature | None
    reflected_overload_signatures: tuple[RuntimeMemberSignature, ...] = ()
    value_type: Type | None = None
    unkeyable: bool = False


@dc.dataclass(frozen=True)
class RuntimeMembersInspection:
    origin: type
    members: tuple[RuntimeMember, ...]
    members_by_name: dict[str, RuntimeMember]


##


def _get_origin_type(obj: object) -> type:
    origin = ta.get_origin(obj)
    if origin is None:
        origin = obj

    if not isinstance(origin, type):
        raise ReflectionTypeError(f'Unsupported member source: {obj!r}')

    return origin


def _iter_mro_members(origin: type) -> ta.Iterator[tuple[str, type, object]]:
    for owner in reversed(origin.__mro__):
        for name, obj in owner.__dict__.items():
            if name.startswith('__') and name.endswith('__'):
                continue
            yield name, owner, obj


def _signature_or_none(obj: object) -> inspect.Signature | None:
    try:
        return inspect.signature(obj)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _make_any() -> AnyType:
    return _ANY_TYPES[TypeOfAny.FROM_OMITTED_GENERICS]


def _drop_first_parameter(signature: RuntimeMemberSignature) -> RuntimeMemberSignature:
    if not signature.parameters:
        return signature
    return RuntimeMemberSignature(signature.parameters[1:], signature.return_type)


@ta.final
class MembersReflector(
    HasKeys,
    HasReflector,
    HasLock,
):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._inspection_cache: dict[object, RuntimeMembersInspection] = {}

    #

    def _reflect_annotation(
            self,
            annotation: object,
            replacements: SubstitutionMap,
    ) -> Type:
        if annotation is inspect.Signature.empty:
            return _make_any()
        typ = self._reflector.reflect_type(annotation)
        if replacements:
            return substitute_type(typ, replacements)
        return typ

    def _reflect_signature(
            self,
            signature: inspect.Signature | None,
            replacements: SubstitutionMap,
    ) -> RuntimeMemberSignature | None:
        if signature is None:
            return None

        parameters: list[RuntimeMemberParameter] = []
        for parameter in signature.parameters.values():
            parameters.append(RuntimeMemberParameter(
                parameter.name,
                parameter.kind,
                self._reflect_annotation(parameter.annotation, replacements),
                parameter.default is not inspect.Parameter.empty,
            ))

        return RuntimeMemberSignature(
            tuple(parameters),
            self._reflect_annotation(signature.return_annotation, replacements),
        )

    def _reflect_overload_signatures(
            self,
            obj: object,
            replacements: SubstitutionMap,
    ) -> tuple[RuntimeMemberSignature, ...]:
        ret: list[RuntimeMemberSignature] = []
        try:
            overloads = ta.get_overloads(obj)  # type: ignore[arg-type]
        except AttributeError:
            return ()

        for overload in overloads:
            reflected = self._reflect_signature(_signature_or_none(overload), replacements)
            if reflected is not None:
                ret.append(reflected)
        return tuple(ret)

    def _make_member(
            self,
            name: str,
            kind: RuntimeMemberKind,
            owner: type,
            obj: object,
            signature: inspect.Signature | None,
            replacements: SubstitutionMap,
    ) -> RuntimeMember:
        try:
            reflected_signature = self._reflect_signature(
                signature,
                replacements,
            )

            reflected_overload_signatures = self._reflect_overload_signatures(
                obj,
                replacements,
            )

        except UnreflectableTypeError:
            return RuntimeMember(
                name,
                kind,
                owner,
                obj,
                signature,
                None,
                unkeyable=True,
            )

        return RuntimeMember(
            name,
            kind,
            owner,
            obj,
            signature,
            reflected_signature,
            reflected_overload_signatures,
        )

    def _classify_member(
            self,
            name: str,
            owner: type,
            replacements: SubstitutionMap,
    ) -> RuntimeMember:
        obj = inspect.getattr_static(owner, name)

        if isinstance(obj, staticmethod):
            fn = obj.__func__
            return self._make_member(
                name,
                RuntimeMemberKind.STATICMETHOD,
                owner,
                obj,
                _signature_or_none(fn),
                replacements,
            )

        if isinstance(obj, classmethod):
            fn = obj.__func__
            return self._make_member(
                name,
                RuntimeMemberKind.CLASSMETHOD,
                owner,
                obj,
                _signature_or_none(fn),
                replacements,
            )

        if isinstance(obj, property):
            return self._make_member(
                name,
                RuntimeMemberKind.PROPERTY,
                owner,
                obj,
                _signature_or_none(obj.fget),
                replacements,
            )

        if isinstance(obj, pytypes.FunctionType):
            return self._make_member(
                name,
                RuntimeMemberKind.FUNCTION,
                owner,
                obj,
                _signature_or_none(obj),
                replacements,
            )

        return self._make_member(
            name,
            RuntimeMemberKind.DATA,
            owner,
            obj,
            _signature_or_none(obj),
            replacements,
        )

    def _get_mro_entries_by_info(self, obj: object) -> dict[object, MroEntry]:
        source_type = self._reflector.reflect_type(obj)
        if not isinstance(source_type, Instance):
            raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
        return {
            entry._info: entry
            for entry in get_mro_entries(source_type)
        }

    def _get_owner_replacements(
            self,
            owner: type,
            entries_by_info: dict[object, MroEntry],
    ) -> SubstitutionMap:
        owner_info = self._reflector.universe.get_type_info(owner)
        entry = entries_by_info.get(owner_info)
        if entry is None or not entry._info._type_vars:
            return {}
        if len(entry._info._type_vars) != len(entry._args):
            raise ReflectionTypeError(
                f'Cannot replace member signature type with mismatched owner args: {entry.instance!r}',
            )
        return dict(zip(entry._info._type_vars, entry._args))

    def inspect_runtime_members(self, obj: object) -> RuntimeMembersInspection:
        try:
            return self._inspection_cache[obj]
        except KeyError:
            pass

        # FIXME: lol lock discipline
        ret = self._inspect_runtime_members_uncached(obj)
        self._inspection_cache[obj] = ret
        return ret

    def _inspect_runtime_members_uncached(
            self,
            obj: object,
    ) -> RuntimeMembersInspection:
        origin = _get_origin_type(obj)
        entries_by_info = self._get_mro_entries_by_info(obj)
        members_by_name: dict[str, RuntimeMember] = {}

        for name, owner, _ in _iter_mro_members(origin):
            members_by_name[name] = self._classify_member(
                name,
                owner,
                self._get_owner_replacements(owner, entries_by_info),
            )

        return RuntimeMembersInspection(origin, tuple(members_by_name.values()), members_by_name)

    def get_member_call_signature(self, member: RuntimeMember) -> RuntimeMemberSignature | None:
        signature = member.reflected_signature
        if signature is None:
            return None

        if member.kind in (RuntimeMemberKind.FUNCTION, RuntimeMemberKind.CLASSMETHOD):
            return _drop_first_parameter(signature)

        if member.kind == RuntimeMemberKind.STATICMETHOD:
            return signature

        return None

    def get_member_call_signatures(self, member: RuntimeMember) -> tuple[RuntimeMemberSignature, ...]:
        if member.reflected_overload_signatures:
            signatures = member.reflected_overload_signatures
        elif (signature := member.reflected_signature) is not None:
            signatures = (signature,)
        else:
            return ()

        if member.kind in (RuntimeMemberKind.FUNCTION, RuntimeMemberKind.CLASSMETHOD):
            return tuple(_drop_first_parameter(signature) for signature in signatures)

        if member.kind == RuntimeMemberKind.STATICMETHOD:
            return signatures

        return ()

    def get_member_value_type(self, member: RuntimeMember) -> Type | None:
        if member.value_type is not None:
            return member.value_type

        signature = member.reflected_signature
        if signature is None:
            return None

        if member.kind == RuntimeMemberKind.PROPERTY:
            return signature.return_type

        return None

    def member_signature_key(
            self,
            signature: RuntimeMemberSignature,
    ) -> TypeKey:
        return TypeKey((
            'member_signature',
            tuple(
                (
                    parameter.name,
                    parameter.kind,
                    self._member_type_key(parameter.typ),
                    parameter.has_default,
                )
                for parameter in signature.parameters
            ),
            self._member_type_key(signature.return_type),
        ))

    def member_structural_signature_key(
            self,
            signature: RuntimeMemberSignature,
    ) -> TypeKey:
        return TypeKey((
            'member_signature',
            tuple(
                (
                    parameter.name,
                    parameter.kind,
                    self._keys.type_key(parameter.typ, 'structural'),
                    parameter.has_default,
                )
                for parameter in signature.parameters
            ),
            self._keys.type_key(signature.return_type, 'structural'),
        ))

    def _member_type_key(self, typ: Type) -> TypeKey:
        cur = typ
        if isinstance(cur, AnnotatedType):
            cur = cur.item
        if isinstance(cur, TypeAliasType):
            cur = get_type_alias_target(cur)
        return self._keys.type_key(cur)

    def get_member_call_signature_key(
            self,
            member: RuntimeMember,
    ) -> TypeKey | None:
        if member.unkeyable:
            raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

        signature = self.get_member_call_signature(member)
        if signature is None:
            return None
        return self.member_signature_key(signature)

    def get_member_call_structural_signature_key(
            self,
            member: RuntimeMember,
    ) -> TypeKey | None:
        if member.unkeyable:
            raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

        signature = self.get_member_call_signature(member)
        if signature is None:
            return None
        return self.member_structural_signature_key(signature)

    def get_member_value_type_key(
            self,
            member: RuntimeMember,
    ) -> TypeKey | None:
        if member.unkeyable:
            raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

        typ = self.get_member_value_type(member)
        if typ is None:
            return None
        return self._member_type_key(typ)

    def get_member_value_structural_type_key(
            self,
            member: RuntimeMember,
    ) -> TypeKey | None:
        if member.unkeyable:
            raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

        typ = self.get_member_value_type(member)
        if typ is None:
            return None
        return self._keys.type_key(typ, 'structural')
