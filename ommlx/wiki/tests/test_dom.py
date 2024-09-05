import abc
import dataclasses as dc
import importlib.resources
import typing as ta  # noqa

import wikitextparser as wtp


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


def test_dom():
    src = importlib.resources.files(__package__).joinpath('test.wiki').read_text()
    wiki = wtp.parse(src)
    print(wiki)
