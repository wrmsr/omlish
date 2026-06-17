# ruff: noqa: SLF001
import dataclasses as dc
import enum
import inspect
import types as pytypes
import typing as ta

from ..core.substitute import SubstitutionMap
from ..core.substitute import substitute_type
from ..core.subtypes import MroEntry
from ..core.typekeys import TypeKey
from ..core.typekeys import type_key
from ..core.types import _ANY_TYPES
from ..core.types import AnyType
from ..core.types import Type
from ..core.types import TypeOfAny
from ..errors import ReflectionTypeError
from ..errors import UnreflectableTypeError
from ..reflector import or_default_reflector
from ..reflector import TypeReflector
from .ops import reflect_mro_entries
from .queries import get_runtime_unaliased_type_key


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


def _reflect_annotation(
        annotation: object,
        reflector: TypeReflector,
        replacements: SubstitutionMap,
) -> Type:
    if annotation is inspect.Signature.empty:
        return _make_any()
    typ = reflector.reflect_type(annotation)
    if replacements:
        return substitute_type(typ, replacements)
    return typ


def _reflect_signature(
        signature: inspect.Signature | None,
        reflector: TypeReflector,
        replacements: SubstitutionMap,
) -> RuntimeMemberSignature | None:
    if signature is None:
        return None

    parameters: list[RuntimeMemberParameter] = []
    for parameter in signature.parameters.values():
        parameters.append(RuntimeMemberParameter(
            parameter.name,
            parameter.kind,
            _reflect_annotation(parameter.annotation, reflector, replacements),
            parameter.default is not inspect.Parameter.empty,
        ))

    return RuntimeMemberSignature(
        tuple(parameters),
        _reflect_annotation(signature.return_annotation, reflector, replacements),
    )


def _reflect_overload_signatures(
        obj: object,
        reflector: TypeReflector,
        replacements: SubstitutionMap,
) -> tuple[RuntimeMemberSignature, ...]:
    ret: list[RuntimeMemberSignature] = []
    try:
        overloads = ta.get_overloads(obj)  # type: ignore[arg-type]
    except AttributeError:
        return ()

    for overload in overloads:
        reflected = _reflect_signature(_signature_or_none(overload), reflector, replacements)
        if reflected is not None:
            ret.append(reflected)
    return tuple(ret)


def _drop_first_parameter(signature: RuntimeMemberSignature) -> RuntimeMemberSignature:
    if not signature.parameters:
        return signature
    return RuntimeMemberSignature(signature.parameters[1:], signature.return_type)


def _make_member(
        name: str,
        kind: RuntimeMemberKind,
        owner: type,
        obj: object,
        signature: inspect.Signature | None,
        reflector: TypeReflector,
        replacements: SubstitutionMap,
) -> RuntimeMember:
    try:
        reflected_signature = _reflect_signature(signature, reflector, replacements)
        reflected_overload_signatures = _reflect_overload_signatures(obj, reflector, replacements)
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
        name: str,
        owner: type,
        reflector: TypeReflector,
        replacements: SubstitutionMap,
) -> RuntimeMember:
    obj = inspect.getattr_static(owner, name)

    if isinstance(obj, staticmethod):
        fn = obj.__func__
        return _make_member(
            name,
            RuntimeMemberKind.STATICMETHOD,
            owner,
            obj,
            _signature_or_none(fn),
            reflector,
            replacements,
        )

    if isinstance(obj, classmethod):
        fn = obj.__func__
        return _make_member(
            name,
            RuntimeMemberKind.CLASSMETHOD,
            owner,
            obj,
            _signature_or_none(fn),
            reflector,
            replacements,
        )

    if isinstance(obj, property):
        return _make_member(
            name,
            RuntimeMemberKind.PROPERTY,
            owner,
            obj,
            _signature_or_none(obj.fget),
            reflector,
            replacements,
        )

    if isinstance(obj, pytypes.FunctionType):
        return _make_member(
            name,
            RuntimeMemberKind.FUNCTION,
            owner,
            obj,
            _signature_or_none(obj),
            reflector,
            replacements,
        )

    return _make_member(
        name,
        RuntimeMemberKind.DATA,
        owner,
        obj,
        _signature_or_none(obj),
        reflector,
        replacements,
    )


def _get_mro_entries_by_info(
        obj: object,
        reflector: TypeReflector,
) -> dict[object, MroEntry]:
    return {
        entry._info: entry
        for entry in reflect_mro_entries(obj, reflector)
    }


def _get_owner_replacements(
        owner: type,
        entries_by_info: dict[object, MroEntry],
        reflector: TypeReflector,
) -> SubstitutionMap:
    owner_info = reflector.universe.get_type_info(owner)
    entry = entries_by_info.get(owner_info)
    if entry is None or not entry._info._type_vars:
        return {}
    if len(entry._info._type_vars) != len(entry._args):
        raise ReflectionTypeError(
            f'Cannot replace member signature type with mismatched owner args: {entry.instance!r}',
        )
    return dict(zip(entry._info._type_vars, entry._args))


def inspect_runtime_members(
        obj: object,
        reflector: TypeReflector | None = None,
) -> RuntimeMembersInspection:
    rt_reflector = or_default_reflector(reflector)
    return ta.cast(RuntimeMembersInspection, rt_reflector.cached_inspection(
        'members',
        obj,
        lambda: _inspect_runtime_members_uncached(obj, rt_reflector),
    ))


def _inspect_runtime_members_uncached(
        obj: object,
        rt_reflector: TypeReflector,
) -> RuntimeMembersInspection:
    origin = _get_origin_type(obj)
    entries_by_info = _get_mro_entries_by_info(obj, rt_reflector)
    members_by_name: dict[str, RuntimeMember] = {}

    for name, owner, _ in _iter_mro_members(origin):
        members_by_name[name] = _classify_member(
            name,
            owner,
            rt_reflector,
            _get_owner_replacements(owner, entries_by_info, rt_reflector),
        )

    return RuntimeMembersInspection(origin, tuple(members_by_name.values()), members_by_name)


def get_member_call_signature(member: RuntimeMember) -> RuntimeMemberSignature | None:
    signature = member.reflected_signature
    if signature is None:
        return None

    if member.kind in (RuntimeMemberKind.FUNCTION, RuntimeMemberKind.CLASSMETHOD):
        return _drop_first_parameter(signature)

    if member.kind == RuntimeMemberKind.STATICMETHOD:
        return signature

    return None


def get_member_call_signatures(member: RuntimeMember) -> tuple[RuntimeMemberSignature, ...]:
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


def get_member_value_type(member: RuntimeMember) -> Type | None:
    if member.value_type is not None:
        return member.value_type

    signature = member.reflected_signature
    if signature is None:
        return None

    if member.kind == RuntimeMemberKind.PROPERTY:
        return signature.return_type

    return None


def member_signature_key(
        signature: RuntimeMemberSignature,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    return TypeKey((
        'member_signature',
        tuple(
            (
                parameter.name,
                parameter.kind,
                _member_type_key(parameter.typ, reflector),
                parameter.has_default,
            )
            for parameter in signature.parameters
        ),
        _member_type_key(signature.return_type, reflector),
    ))


def member_structural_signature_key(
        signature: RuntimeMemberSignature,
        reflector: TypeReflector,
) -> TypeKey:
    return TypeKey((
        'member_signature',
        tuple(
            (
                parameter.name,
                parameter.kind,
                reflector.structural_type_key(parameter.typ),
                parameter.has_default,
            )
            for parameter in signature.parameters
        ),
        reflector.structural_type_key(signature.return_type),
    ))


def _member_type_key(typ: Type, reflector: TypeReflector | None) -> TypeKey:
    if reflector is None:
        return type_key(typ)
    return get_runtime_unaliased_type_key(typ, reflector)


def get_member_call_signature_key(
        member: RuntimeMember,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    if member.unkeyable:
        raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

    signature = get_member_call_signature(member)
    if signature is None:
        return None
    return member_signature_key(signature, reflector)


def get_member_call_structural_signature_key(
        member: RuntimeMember,
        reflector: TypeReflector,
) -> TypeKey | None:
    if member.unkeyable:
        raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

    signature = get_member_call_signature(member)
    if signature is None:
        return None
    return member_structural_signature_key(signature, reflector)


def get_member_value_type_key(
        member: RuntimeMember,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    if member.unkeyable:
        raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

    typ = get_member_value_type(member)
    if typ is None:
        return None
    return _member_type_key(typ, reflector)


def get_member_value_structural_type_key(
        member: RuntimeMember,
        reflector: TypeReflector,
) -> TypeKey | None:
    if member.unkeyable:
        raise ReflectionTypeError(f'Member is not keyable: {member.name!r}')

    typ = get_member_value_type(member)
    if typ is None:
        return None
    return reflector.structural_type_key(typ)
