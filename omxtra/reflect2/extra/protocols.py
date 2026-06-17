# ruff: noqa: SLF001
import dataclasses as dc
import enum
import inspect
import typing as ta

from ..core.substitute import SubstitutionMap
from ..core.substitute import substitute_type
from ..core.subtypes import MroEntry
from ..core.subtypes import is_subtype
from ..core.typekeys import TypeKey
from ..core.types import Type
from ..errors import ProtocolReflectionError
from ..errors import ReflectionError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import TypeReflector
from .members import RuntimeMember
from .members import RuntimeMemberKind
from .members import RuntimeMembersInspection
from .members import get_member_call_signature_key
from .members import get_member_call_structural_signature_key
from .members import get_member_value_structural_type_key
from .members import get_member_value_type
from .members import get_member_value_type_key
from .members import inspect_runtime_members
from .ops import reflect_mro_entries
from .queries import get_runtime_unaliased_type_key
from .records import inspect_record_or_none


##


@dc.dataclass(frozen=True)
class RuntimeProtocolInspection:
    origin: type
    members: tuple[RuntimeMember, ...]
    members_by_name: dict[str, RuntimeMember]
    member_keys: dict[str, TypeKey]
    member_structural_keys: dict[str, TypeKey]


class ProtocolImplementationIssueReason(enum.Enum):
    MISSING = 'missing'
    MISMATCH = 'mismatch'
    UNKEYABLE = 'unkeyable'


@dc.dataclass(frozen=True)
class ProtocolImplementationIssue:
    member: str
    reason: ProtocolImplementationIssueReason


##


def _get_reflector(reflector: TypeReflector | None) -> TypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def _get_origin_protocol(obj: object) -> type:
    origin = ta.get_origin(obj)
    if origin is None:
        origin = obj

    if not is_protocol(origin):
        raise ProtocolReflectionError(f'Unsupported protocol source: {obj!r}')

    return origin  # type: ignore[return-value]


def is_protocol(obj: object) -> bool:
    return isinstance(obj, type) and bool(getattr(obj, '_is_protocol', False))


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
        raise ProtocolReflectionError(
            f'Cannot replace protocol member type with mismatched owner args: {entry._instance!r}',
        )
    return dict(zip(entry._info._type_vars, entry._args))


def _reflect_annotation(
        annotation: object,
        replacements: SubstitutionMap,
        reflector: TypeReflector,
) -> Type:
    typ = reflector.reflect_type(annotation)
    if replacements:
        return substitute_type(typ, replacements)
    return typ


def _iter_protocol_annotation_members(origin: type) -> ta.Iterator[tuple[str, type, object]]:
    for owner in reversed(origin.__mro__):
        if not is_protocol(owner):
            continue
        annotations = getattr(owner, '__annotations__', {})
        if not isinstance(annotations, dict):
            raise ProtocolReflectionError(f'Unsupported protocol annotations for {owner!r}: {annotations!r}')
        for name, annotation in annotations.items():
            if name.startswith('_'):
                continue
            yield name, owner, annotation


def _make_annotation_member(
        name: str,
        owner: type,
        annotation: object,
        entries_by_info: dict[object, MroEntry],
        reflector: TypeReflector,
) -> RuntimeMember:
    return RuntimeMember(
        name,
        RuntimeMemberKind.DATA,
        owner,
        inspect.Signature.empty,
        None,
        None,
        value_type=_reflect_annotation(
            annotation,
            _get_owner_replacements(owner, entries_by_info, reflector),
            reflector,
        ),
    )


def _filter_runtime_members(inspection: RuntimeMembersInspection) -> dict[str, RuntimeMember]:
    return {
        name: member
        for name, member in inspection.members_by_name.items()
        if not name.startswith('_')
    }


def inspect_protocol_members(
        obj: object,
        reflector: TypeReflector | None = None,
) -> RuntimeProtocolInspection:
    rt_reflector = _get_reflector(reflector)
    return ta.cast(RuntimeProtocolInspection, rt_reflector.cached_inspection(
        'protocol',
        obj,
        lambda: _inspect_protocol_members_uncached(obj, rt_reflector),
    ))


def _inspect_protocol_members_uncached(
        obj: object,
        rt_reflector: TypeReflector,
) -> RuntimeProtocolInspection:
    origin = _get_origin_protocol(obj)
    entries_by_info = _get_mro_entries_by_info(obj, rt_reflector)

    members_by_name = _filter_runtime_members(inspect_runtime_members(obj, rt_reflector))
    for name, owner, annotation in _iter_protocol_annotation_members(origin):
        if name not in members_by_name:
            members_by_name[name] = _make_annotation_member(name, owner, annotation, entries_by_info, rt_reflector)

    return RuntimeProtocolInspection(
        origin,
        tuple(members_by_name.values()),
        members_by_name,
        get_protocol_member_keys(members_by_name, rt_reflector),
        get_protocol_member_structural_keys(members_by_name, rt_reflector),
    )


def get_protocol_member_key(
        member: RuntimeMember,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    key = get_member_call_signature_key(member, reflector)
    if key is not None:
        return key

    key = get_member_value_type_key(member, reflector)
    if key is not None:
        return key

    raise ProtocolReflectionError(f'Protocol member is not keyable: {member.name!r}')


def get_protocol_member_keys(
        members_by_name: dict[str, RuntimeMember],
        reflector: TypeReflector | None = None,
) -> dict[str, TypeKey]:
    return {
        name: get_protocol_member_key(member, reflector)
        for name, member in members_by_name.items()
    }


def get_protocol_member_structural_key(
        member: RuntimeMember,
        reflector: TypeReflector,
) -> TypeKey:
    key = get_member_call_structural_signature_key(member, reflector)
    if key is not None:
        return key

    key = get_member_value_structural_type_key(member, reflector)
    if key is not None:
        return key

    raise ProtocolReflectionError(f'Protocol member is not keyable: {member.name!r}')


def get_protocol_member_structural_keys(
        members_by_name: dict[str, RuntimeMember],
        reflector: TypeReflector,
) -> dict[str, TypeKey]:
    return {
        name: get_protocol_member_structural_key(member, reflector)
        for name, member in members_by_name.items()
    }


def _get_concrete_member_keys(
        obj: object,
        reflector: TypeReflector,
) -> dict[str, TypeKey]:
    keys: dict[str, TypeKey] = {}

    if (record := inspect_record_or_none(obj, reflector)) is not None:
        keys.update({
            name: get_runtime_unaliased_type_key(field.typ, reflector)
            for name, field in record.fields_by_name.items()
        })

    members = inspect_runtime_members(obj, reflector)
    for name, member in members.members_by_name.items():
        key = get_member_call_signature_key(member, reflector)
        if key is None:
            key = get_member_value_type_key(member, reflector)
        if key is not None:
            keys[name] = key

    return keys


def _get_concrete_runtime_members(
        obj: object,
        reflector: TypeReflector,
) -> dict[str, RuntimeMember]:
    return inspect_runtime_members(obj, reflector).members_by_name


def _get_concrete_member_keys_or_issues(
        obj: object,
        reflector: TypeReflector,
) -> tuple[dict[str, TypeKey], list[ProtocolImplementationIssue]]:
    issues: list[ProtocolImplementationIssue] = []
    keys: dict[str, TypeKey] = {}

    try:
        if (record := inspect_record_or_none(obj, reflector)) is not None:
            keys.update({
                name: get_runtime_unaliased_type_key(field.typ, reflector)
                for name, field in record.fields_by_name.items()
            })
    except ReflectionError:
        issues.append(ProtocolImplementationIssue('*', ProtocolImplementationIssueReason.UNKEYABLE))

    members = inspect_runtime_members(obj, reflector)
    for name, member in members.members_by_name.items():
        try:
            key = get_member_call_signature_key(member, reflector)
            if key is None:
                key = get_member_value_type_key(member, reflector)
        except ReflectionError:
            issues.append(ProtocolImplementationIssue(name, ProtocolImplementationIssueReason.UNKEYABLE))
            continue
        if key is not None:
            keys[name] = key

    return keys, issues


def _property_members_match(protocol_member: RuntimeMember, concrete_member: RuntimeMember) -> bool | None:
    if protocol_member.kind != RuntimeMemberKind.PROPERTY or concrete_member.kind != RuntimeMemberKind.PROPERTY:
        return None

    protocol_type = get_member_value_type(protocol_member)
    concrete_type = get_member_value_type(concrete_member)
    if protocol_type is None or concrete_type is None:
        raise ProtocolReflectionError(f'Protocol property member is not comparable: {protocol_member.name!r}')

    return is_subtype(concrete_type, protocol_type)


def is_protocol_implemented_by(
        concrete: object,
        protocol: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    protocol_inspection = inspect_protocol_members(protocol, rt_reflector)
    concrete_keys = _get_concrete_member_keys(concrete, rt_reflector)
    concrete_members = _get_concrete_runtime_members(concrete, rt_reflector)

    for name, protocol_key in protocol_inspection.member_keys.items():
        if (protocol_member := protocol_inspection.members_by_name.get(name)) is not None:
            concrete_member = concrete_members.get(name)
            if concrete_member is not None:
                property_match = _property_members_match(protocol_member, concrete_member)
                if property_match is not None:
                    if property_match:
                        continue
                    return False

        if concrete_keys.get(name) != protocol_key:
            return False

    return True


def check_protocol_implementation(
        concrete: object,
        protocol: object,
        reflector: TypeReflector | None = None,
) -> list[ProtocolImplementationIssue]:
    rt_reflector = _get_reflector(reflector)
    try:
        protocol_inspection = inspect_protocol_members(protocol, rt_reflector)
    except ReflectionError:
        return [ProtocolImplementationIssue('*', ProtocolImplementationIssueReason.UNKEYABLE)]

    concrete_keys, issues = _get_concrete_member_keys_or_issues(concrete, rt_reflector)
    concrete_members = _get_concrete_runtime_members(concrete, rt_reflector)

    for name, protocol_key in protocol_inspection.member_keys.items():
        if (protocol_member := protocol_inspection.members_by_name.get(name)) is not None:
            concrete_member = concrete_members.get(name)
            if concrete_member is not None:
                try:
                    property_match = _property_members_match(protocol_member, concrete_member)
                except ReflectionError:
                    issues.append(ProtocolImplementationIssue(name, ProtocolImplementationIssueReason.UNKEYABLE))
                    continue
                if property_match is not None:
                    if not property_match:
                        issues.append(ProtocolImplementationIssue(name, ProtocolImplementationIssueReason.MISMATCH))
                    continue

        try:
            concrete_key = concrete_keys[name]
        except KeyError:
            issues.append(ProtocolImplementationIssue(name, ProtocolImplementationIssueReason.MISSING))
            continue
        if concrete_key != protocol_key:
            issues.append(ProtocolImplementationIssue(name, ProtocolImplementationIssueReason.MISMATCH))

    return issues


def is_protocol_implemented_by_or_false(
        concrete: object,
        protocol: object,
        reflector: TypeReflector | None = None,
) -> bool:
    return not check_protocol_implementation(concrete, protocol, reflector)
