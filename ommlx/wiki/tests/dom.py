"""
Text
Wikilink
ExternalLink
Html
Comment

Argument
Heading
HtmlEntity
Tag
Template
"""
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
    title: str
    text: str


@dc.dataclass(frozen=True)
class ExternalLink(Dom):
    title: str
    url: str


@dc.dataclass(frozen=True)
class Html(Dom):
    s: str


@dc.dataclass(frozen=True)
class Comment:
    s: str
