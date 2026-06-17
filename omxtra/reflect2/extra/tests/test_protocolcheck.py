# ruff: noqa: F821 PLC0132 SLF001
import dataclasses as dc
import typing as ta

import pytest

from ...core import types
from ...errors import UnreflectableTypeError
from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from ..protocols import ProtocolImplementationIssueReason
from ..protocols import check_protocol_implementation
from ..protocols import is_protocol_implemented_by
from ..protocols import is_protocol_implemented_by_or_false


def _make_reflector() -> RuntimeTypeReflector:
    return RuntimeTypeReflector(RuntimeTypeUniverse())


def test_protocol_check_accepts_matching_method() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    class Concrete:
        def read(self) -> bytes:
            return b''

    assert is_protocol_implemented_by(Concrete, Reader, _make_reflector())


def test_protocol_check_preserves_literal_new_type_identity_for_methods() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    class HasMode(ta.Protocol):
        def set_mode(self, mode: mode) -> mode:
            ...

    class Matching:
        def set_mode(self, mode: mode) -> mode:
            return mode

    class Mismatched:
        def set_mode(self, mode: other_mode) -> other_mode:
            return mode

    reflector = _make_reflector()

    assert is_protocol_implemented_by(Matching, HasMode, reflector)
    assert check_protocol_implementation(Matching, HasMode, reflector) == []
    assert not is_protocol_implemented_by(Mismatched, HasMode, reflector)
    issues = check_protocol_implementation(Mismatched, HasMode, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('set_mode', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_rejects_mismatched_method_return() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    class Concrete:
        def read(self) -> str:
            return ''

    assert not is_protocol_implemented_by(Concrete, Reader, _make_reflector())
    issues = check_protocol_implementation(Concrete, Reader, _make_reflector())
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('read', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_rejects_missing_member() -> None:
    class Reader(ta.Protocol):
        def read(self) -> bytes:
            ...

    class Concrete:
        pass

    assert not is_protocol_implemented_by(Concrete, Reader, _make_reflector())
    issues = check_protocol_implementation(Concrete, Reader, _make_reflector())
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('read', ProtocolImplementationIssueReason.MISSING),
    ]


def test_protocol_check_reports_multiple_simultaneous_issues() -> None:
    class NeedsSeveral(ta.Protocol):
        name: str

        def read(self) -> bytes:
            ...

        def close(self) -> None:
            ...

    @dc.dataclass
    class Concrete:
        name: int

        def read(self) -> str:
            return ''

    issues = check_protocol_implementation(Concrete, NeedsSeveral, _make_reflector())

    assert set((issue.member, issue.reason) for issue in issues) == {  # noqa
        ('name', ProtocolImplementationIssueReason.MISMATCH),
        ('read', ProtocolImplementationIssueReason.MISMATCH),
        ('close', ProtocolImplementationIssueReason.MISSING),
    }


def test_protocol_check_reports_concrete_unkeyable_member() -> None:
    class HasValue(ta.Protocol):
        value: int

    class Concrete:
        @property
        def value(self) -> 'Missing':  # type: ignore  # noqa
            return 1

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=lambda name: types.UnboundType(name))

    issues = check_protocol_implementation(Concrete, HasValue, reflector)

    assert [(issue.member, issue.reason) for issue in issues] == [
        ('value', ProtocolImplementationIssueReason.UNKEYABLE),
        ('value', ProtocolImplementationIssueReason.MISSING),
    ]


def test_protocol_check_accepts_matching_dataclass_field() -> None:
    class HasName(ta.Protocol):
        name: str

    @dc.dataclass
    class Concrete:
        name: str

    assert is_protocol_implemented_by(Concrete, HasName, _make_reflector())
    assert check_protocol_implementation(Concrete, HasName, _make_reflector()) == []
    assert is_protocol_implemented_by_or_false(Concrete, HasName, _make_reflector())


def test_protocol_check_preserves_literal_new_type_identity_for_data_members() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    class HasMode(ta.Protocol):
        mode: ta.Any

    HasMode.__annotations__['mode'] = mode

    @dc.dataclass
    class Matching:
        mode: ta.Any

    Matching.__annotations__['mode'] = mode

    @dc.dataclass
    class Mismatched:
        mode: ta.Any

    Mismatched.__annotations__['mode'] = other_mode

    reflector = _make_reflector()

    assert is_protocol_implemented_by(Matching, HasMode, reflector)
    assert check_protocol_implementation(Matching, HasMode, reflector) == []
    assert not is_protocol_implemented_by(Mismatched, HasMode, reflector)
    issues = check_protocol_implementation(Mismatched, HasMode, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('mode', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_expands_alias_new_type_literal_data_members() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class HasModes(ta.Protocol):
        modes: ta.Any

    HasModes.__annotations__['modes'] = mode_list

    @dc.dataclass
    class Matching:
        modes: list[mode]  # noqa

    @dc.dataclass
    class Mismatched:
        modes: list[other_mode]  # noqa

    reflector = _make_reflector()

    assert is_protocol_implemented_by(Matching, HasModes, reflector)
    assert check_protocol_implementation(Matching, HasModes, reflector) == []
    assert not is_protocol_implemented_by(Mismatched, HasModes, reflector)
    issues = check_protocol_implementation(Mismatched, HasModes, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('modes', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_expands_alias_new_type_literal_method_signatures() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class HasModes(ta.Protocol):
        def set_modes(self, modes: mode_list) -> mode_list:  # type: ignore
            ...

    class Matching:
        def set_modes(self, modes: list[mode]) -> list[mode]:  # noqa
            return modes

    class Mismatched:
        def set_modes(self, modes: list[other_mode]) -> list[other_mode]:  # noqa
            return modes

    reflector = _make_reflector()

    assert is_protocol_implemented_by(Matching, HasModes, reflector)
    assert check_protocol_implementation(Matching, HasModes, reflector) == []
    assert not is_protocol_implemented_by(Mismatched, HasModes, reflector)
    issues = check_protocol_implementation(Mismatched, HasModes, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('set_modes', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_rejects_mismatched_dataclass_field() -> None:
    class HasName(ta.Protocol):
        name: str

    @dc.dataclass
    class Concrete:
        name: int

    assert not is_protocol_implemented_by(Concrete, HasName, _make_reflector())


def test_protocol_check_accepts_matching_property_value_type() -> None:
    class HasName(ta.Protocol):
        name: str

    class Concrete:
        @property
        def name(self) -> str:
            return ''

    assert is_protocol_implemented_by(Concrete, HasName, _make_reflector())


def test_protocol_check_accepts_covariant_property_value_type() -> None:
    class HasValue(ta.Protocol):
        @property
        def value(self) -> object:
            ...

    class Concrete:
        @property
        def value(self) -> int:
            return 1

    assert is_protocol_implemented_by(Concrete, HasValue, _make_reflector())
    assert check_protocol_implementation(Concrete, HasValue, _make_reflector()) == []


def test_protocol_check_rejects_reversed_property_covariance() -> None:
    class HasValue(ta.Protocol):
        @property
        def value(self) -> int:
            ...

    class Concrete:
        @property
        def value(self) -> object:
            return object()

    assert not is_protocol_implemented_by(Concrete, HasValue, _make_reflector())
    issues = check_protocol_implementation(Concrete, HasValue, _make_reflector())
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('value', ProtocolImplementationIssueReason.MISMATCH),
    ]


def test_protocol_check_keeps_dataclass_data_field_exact_for_now() -> None:
    class HasValue(ta.Protocol):
        value: object

    @dc.dataclass
    class Concrete:
        value: int

    assert not is_protocol_implemented_by(Concrete, HasValue, _make_reflector())


def test_protocol_check_accepts_generic_protocol_method() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class BoxLike(ta.Protocol[t_var]):  # type: ignore
        def get(self) -> t_var:  # type: ignore
            ...

    class IntBox:
        def get(self) -> int:
            return 1

    assert is_protocol_implemented_by(IntBox, BoxLike[int], _make_reflector())  # type: ignore
    assert not is_protocol_implemented_by(IntBox, BoxLike[str], _make_reflector())  # type: ignore


def test_protocol_check_accepts_generic_protocol_data_member() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class HasValue(ta.Protocol[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class IntValue:
        value: int

    assert is_protocol_implemented_by(IntValue, HasValue[int], _make_reflector())  # type: ignore
    assert not is_protocol_implemented_by(IntValue, HasValue[str], _make_reflector())  # type: ignore


def test_protocol_check_raises_for_unkeyable_protocol_member() -> None:
    class HasMissing(ta.Protocol):
        value: 'Missing'  # type: ignore  # noqa

    @dc.dataclass
    class Concrete:
        value: int

    with pytest.raises(UnreflectableTypeError):
        is_protocol_implemented_by(
            Concrete,
            HasMissing,
            RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=lambda name: types.UnboundType(name)),
        )


def test_protocol_check_or_false_handles_unkeyable_protocol_member() -> None:
    class HasMissing(ta.Protocol):
        value: 'Missing'  # type: ignore  # noqa

    @dc.dataclass
    class Concrete:
        value: int

    reflector = RuntimeTypeReflector(RuntimeTypeUniverse(), forward_ref_resolver=lambda name: types.UnboundType(name))

    assert not is_protocol_implemented_by_or_false(Concrete, HasMissing, reflector)
    issues = check_protocol_implementation(Concrete, HasMissing, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('*', ProtocolImplementationIssueReason.UNKEYABLE),
    ]


def test_protocol_check_fails_closed_for_unreflectable_alias_protocol_annotation() -> None:
    bad_alias = ta.TypeAliasType('BadAlias', ta.TypeIs[int])  # type: ignore

    class HasValue(ta.Protocol):
        value: ta.Any

    HasValue.__annotations__['value'] = bad_alias

    @dc.dataclass
    class Concrete:
        value: int

    reflector = _make_reflector()

    with pytest.raises(UnreflectableTypeError):
        is_protocol_implemented_by(Concrete, HasValue, reflector)
    issues = check_protocol_implementation(Concrete, HasValue, reflector)
    assert [(issue.member, issue.reason) for issue in issues] == [
        ('*', ProtocolImplementationIssueReason.UNKEYABLE),
    ]
    assert ('protocol', HasValue) not in reflector._inspection_cache
