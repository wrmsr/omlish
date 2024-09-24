import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class ManifestOrigin:
    module: str
    attr: str

    file: str
    line: int


@dc.dataclass(frozen=True)
class Manifest(ManifestOrigin):
    value: ta.Any
