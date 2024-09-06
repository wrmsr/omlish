"""
TODO:
 - Argument
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


##


class Builder:
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
        match n:
            case mfn.Comment(contents=s):
                return Comment(s)

            case mfn.Text(value=s):
                return Text(s)

            case mfn.Template(name=na, params=ps):
                return Template(
                    self.build_nodes(na),
                    list(map(self.build_parameter, ps)),
                )

            case mfn.Wikilink(title=ti, text=tx):
                return WikiLink(
                    self.build_nodes(ti),
                    self.build_nodes(tx),
                )

            case mfn.ExternalLink(title=ti, url=u):
                return ExternalLink(
                    self.build_nodes(ti),
                    self.build_nodes(u),
                )

            case mfn.HTMLEntity(value=s):
                return Html(s)

            case mfn.Tag(tag=l, contents=c, closing_tag=r, attributes=ats):
                return Tag(
                    self.build_nodes(l),
                    list(map(self.build_attribute, ats)),
                    self.build_nodes(c),
                    self.build_nodes(r),
                )

            case mfn.Heading(title=ti, level=l):
                return Heading(
                    self.build_nodes(ti),
                    l,
                )

            case _:
                raise TypeError(n)

    def build_nodes(self, w: Wikicode | ta.Iterable[mfn.Node] | None) -> Nodes:
        if w is None:
            return ()

        elif isinstance(w, Wikicode):
            return [self.build_node(c) for c in w.nodes]

        elif isinstance(w, ta.Iterable):
            return [self.build_node(c) for c in w]

        else:
            raise TypeError(w)
