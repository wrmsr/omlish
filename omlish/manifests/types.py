# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class ManifestOrigin:
    module: str  # Always starts with exactly one '.'
    attr: ta.Optional[str]  # None if inline

    file: str
    line: int


@dc.dataclass(frozen=True)
class Manifest(ManifestOrigin):
    value: ta.Any  # [{class_key: value_dct}], where class_key is of the form `!.foo.bar.Class` or `!baz.quz.Class`
