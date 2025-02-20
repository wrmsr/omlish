# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class ManifestOrigin:
    module: str
    attr: ta.Optional[str]  # None if inline

    file: str
    line: int


@dc.dataclass(frozen=True)
class Manifest(ManifestOrigin):
    value: ta.Any
