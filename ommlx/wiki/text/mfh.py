"""
TODO:
 - Argument

https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes
"""
import abc
import dataclasses as dc
import typing as ta

import mwparserfromhell as mfh
import mwparserfromhell.nodes as mfn


Wikicode: ta.TypeAlias = mfh.wikicode.Wikicode


##


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
class Parameter:
    name: Nodes
    value: Nodes


@dc.dataclass(frozen=True)
class Template(Node):
    name: Nodes
    params: ta.Sequence[Parameter]


@dc.dataclass(frozen=True)
class Attribute:
    name: Nodes
    value: Nodes


@dc.dataclass(frozen=True)
class Tag(Node):
    l: Nodes
    atts: ta.Sequence[Attribute]
    body: Nodes
    r: Nodes


@dc.dataclass(frozen=True)
class Heading(Node):
    title: Nodes
    level: int


@dc.dataclass(frozen=True)
class Argument(Node):
    name: Nodes
    default: Nodes


##


class NodeBuilder:
    def build_parameter(self, n: mfn.extras.Parameter) -> Parameter:
        if not isinstance(n, mfn.extras.Parameter):
            raise TypeError(n)

        return Parameter(
            self.build_nodes(n.name),
            self.build_nodes(n.value),
        )

    def build_attribute(self, n: mfn.extras.Attribute) -> Attribute:
        if not isinstance(n, mfn.extras.Attribute):
            raise TypeError(n)

        return Attribute(
            self.build_nodes(n.name),
            self.build_nodes(n.value),
        )

    def build_node(self, n: mfn.Node | mfn.extras.Parameter) -> Node:
        if isinstance(n, mfn.Comment):
            return Comment(n.contents)

        elif isinstance(n, mfn.Text):
            return Text(n.value)

        elif isinstance(n, mfn.Template):
            return Template(
                self.build_nodes(n.name),
                list(map(self.build_parameter, n.params)),
            )

        elif isinstance(n, mfn.Wikilink):
            return WikiLink(
                self.build_nodes(n.title),
                self.build_nodes(n.text),
            )

        elif isinstance(n, mfn.ExternalLink):
            return ExternalLink(
                self.build_nodes(n.title),
                self.build_nodes(n.url),
            )

        elif isinstance(n, mfn.HTMLEntity):
            return Html(n.value)

        elif isinstance(n, mfn.Tag):
            return Tag(
                self.build_nodes(n.tag),
                list(map(self.build_attribute, n.attributes)),
                self.build_nodes(n.contents),
                self.build_nodes(n.closing_tag),
            )

        elif isinstance(n, mfn.Heading):
            return Heading(
                self.build_nodes(n.title),
                n.level,
            )

        elif isinstance(n, mfn.Argument):
            return Argument(
                self.build_nodes(n.name),
                self.build_nodes(n.default),
            )

        else:
            raise TypeError(n)

    def build_nodes(self, w: Wikicode | ta.Iterable[mfn.Node] | None) -> Nodes:
        if w is None:
            return ()

        elif isinstance(w, Wikicode):  # type: ignore
            return [self.build_node(c) for c in w.nodes]

        elif isinstance(w, ta.Iterable):
            return [self.build_node(c) for c in w]

        else:
            raise TypeError(w)


##


parse = mfh.parse


def parse_nodes(s: str) -> Nodes:
    wiki = parse(s)
    return NodeBuilder().build_nodes(wiki)
