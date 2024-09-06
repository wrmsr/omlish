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
class Node(abc.ABC):  # noqa
    pass


Nodes: ta.TypeAlias = ta.Sequence[Node]


@dc.dataclass(frozen=True)
class Text(Node):
    s: str


@dc.dataclass(frozen=True)
class WikiLink(Node):
    title: Nodes
    text: Nodes


@dc.dataclass(frozen=True)
class ExternalLink(Node):
    title: Nodes
    url: Nodes


@dc.dataclass(frozen=True)
class Html(Node):
    s: str


@dc.dataclass(frozen=True)
class Comment(Node):
    s: str


@dc.dataclass(frozen=True)
class Parameter(Node):
    name: Nodes
    value: Nodes


@dc.dataclass(frozen=True)
class Template(Node):
    name: Nodes
    params: ta.Sequence[Parameter]
