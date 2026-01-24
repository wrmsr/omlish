import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content


##


class Op(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class From(Op):
    spec: str


@dc.dataclass(frozen=True)
class Section(Op):
    header: str | None
    body: ta.Sequence[Op]


@dc.dataclass(frozen=True)
class Env(Op):
    items: ta.Iterable[tuple[str, str]]


@dc.dataclass(frozen=True, kw_only=True)
class Copy(Op):
    src: str
    dst: str


@dc.dataclass(frozen=True)
class Write(Op):
    path: str
    content: Content

    _: dc.KW_ONLY

    append: bool = False


@dc.dataclass(frozen=True)
class Run(Op):
    body: Content

    _: dc.KW_ONLY

    cache_mounts: ta.Sequence[str] | None = None


@dc.dataclass(frozen=True)
class Workdir(Op):
    path: str


@dc.dataclass(frozen=True)
class Entrypoint(Op):
    parts: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Cmd(Op):
    parts: ta.Sequence[str]
