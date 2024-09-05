import abc
import dataclasses as dc
import typing as ta  # noqa


@dc.dataclass(frozen=True)
class Dom(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class Text(Dom):
    s: str


@dc.dataclass(frozen=True)
class WikiLink(Dom):
    pass


@dc.dataclass(frozen=True)
class ExternalLink(Dom):
    pass
