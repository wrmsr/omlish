"""
Text
Wikilink
ExternalLink
Html
Comment

Argument
Heading
Tag
Template
"""
import abc
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Doc:
    es: ta.Sequence['Dom']


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
class Comment(Dom):
    s: str


@dc.dataclass(frozen=True)
class Parameter(Dom):
    name: str
    value: Text


@dc.dataclass(frozen=True)
class Template(Dom):
    params: ta.Sequence[Parameter]
