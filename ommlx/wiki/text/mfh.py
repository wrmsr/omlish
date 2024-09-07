"""
TODO:
 - Argument

https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes
"""
import abc
import operator
import typing as ta

import mwparserfromhell as mfh
import mwparserfromhell.nodes as mfn

from omlish import dataclasses as dc
from omlish import marshal as msh


Wikicode: ta.TypeAlias = mfh.wikicode.Wikicode


##


@dc.field_modifier
def _omit_field_if_empty(f: dc.Field) -> dc.Field:
    return dc.update_field_metadata(
        f,
        {
            msh.FieldMetadata: msh.FieldMetadata(
                omit_if=operator.not_,
            ),
        },
    )


##


@dc.dataclass(frozen=True)
class Node(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class ContentNode(Node, abc.ABC):  # noqa
    pass


Content: ta.TypeAlias = ta.Sequence[ContentNode]


@dc.dataclass(frozen=True)
class Doc(Node):
    body: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Text(ContentNode):
    s: str


@dc.dataclass(frozen=True)
class WikiLink(ContentNode):
    title: Content = dc.field(default=()) | _omit_field_if_empty
    text: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class ExternalLink(ContentNode):
    title: Content = dc.field(default=()) | _omit_field_if_empty
    url: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Html(ContentNode):
    s: str


@dc.dataclass(frozen=True)
class Comment(ContentNode):
    s: str


@dc.dataclass(frozen=True)
class Parameter(Node):
    name: Content = dc.field(default=()) | _omit_field_if_empty
    value: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Template(ContentNode):
    name: Content = dc.field(default=()) | _omit_field_if_empty
    params: ta.Sequence[Parameter] = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Attribute(Node):
    name: Content = dc.field(default=()) | _omit_field_if_empty
    value: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Tag(ContentNode):
    l: Content = dc.field(default=()) | _omit_field_if_empty
    atts: ta.Sequence[Attribute] = dc.field(default=()) | _omit_field_if_empty
    body: Content = dc.field(default=()) | _omit_field_if_empty
    r: Content = dc.field(default=()) | _omit_field_if_empty


@dc.dataclass(frozen=True)
class Heading(ContentNode):
    title: Content = dc.field(default=()) | _omit_field_if_empty
    level: int = 0


@dc.dataclass(frozen=True)
class Argument(ContentNode):
    name: Content = dc.field(default=()) | _omit_field_if_empty
    default: Content = dc.field(default=()) | _omit_field_if_empty


##


_TRAVERSAL_ATTRS_BY_TYPE: ta.Mapping[type[Node], ta.Sequence[str]] = {
    Doc: ['body'],
    Text: [],
    WikiLink: ['title', 'text'],
    ExternalLink: ['title', 'url'],
    Html: [],
    Comment: [],
    Parameter: ['name', 'value'],
    Template: ['name', 'params'],
    Attribute: ['name', 'value'],
    Tag: ['l', 'atts', 'body', 'r'],
    Heading: ['title'],
    Argument: ['name', 'default'],
}


def traverse_node(root: Node) -> ta.Iterator[tuple[ta.Sequence[tuple[Node, str]], Node]]:
    path: list[tuple[Node, str]] = []

    def rec(n: Node) -> ta.Iterator[tuple[ta.Sequence[tuple[Node, str]], Node]]:
        yield (path, n)

        for a in _TRAVERSAL_ATTRS_BY_TYPE[n.__class__]:
            if not (v := getattr(n, a)):
                continue

            path.append((n, a))
            for c in v:
                yield from rec(c)
            path.pop()

    yield from rec(root)


##


class NodeBuilder:
    def build_parameter(self, n: mfn.extras.Parameter) -> Parameter:
        if not isinstance(n, mfn.extras.Parameter):
            raise TypeError(n)

        return Parameter(
            self.build_content(n.name),
            self.build_content(n.value),
        )

    def build_attribute(self, n: mfn.extras.Attribute) -> Attribute:
        if not isinstance(n, mfn.extras.Attribute):
            raise TypeError(n)

        return Attribute(
            self.build_content(n.name),
            self.build_content(n.value),
        )

    def build_content_node(self, n: mfn.Node) -> ContentNode:
        if isinstance(n, mfn.Comment):
            return Comment(n.contents)

        elif isinstance(n, mfn.Text):
            return Text(n.value)

        elif isinstance(n, mfn.Template):
            return Template(
                self.build_content(n.name),
                list(map(self.build_parameter, n.params)),
            )

        elif isinstance(n, mfn.Wikilink):
            return WikiLink(
                self.build_content(n.title),
                self.build_content(n.text),
            )

        elif isinstance(n, mfn.ExternalLink):
            return ExternalLink(
                self.build_content(n.title),
                self.build_content(n.url),
            )

        elif isinstance(n, mfn.HTMLEntity):
            return Html(n.value)

        elif isinstance(n, mfn.Tag):
            return Tag(
                self.build_content(n.tag),
                list(map(self.build_attribute, n.attributes)),
                self.build_content(n.contents),
                self.build_content(n.closing_tag),
            )

        elif isinstance(n, mfn.Heading):
            return Heading(
                self.build_content(n.title),
                n.level,
            )

        elif isinstance(n, mfn.Argument):
            return Argument(
                self.build_content(n.name),
                self.build_content(n.default),
            )

        else:
            raise TypeError(n)

    def build_content(self, w: Wikicode | ta.Iterable[mfn.Node] | None) -> Content:
        if w is None:
            return ()

        elif isinstance(w, Wikicode):  # type: ignore
            return [self.build_content_node(c) for c in w.nodes]

        elif isinstance(w, ta.Iterable):
            return [self.build_content_node(c) for c in w]

        else:
            raise TypeError(w)


##


parse = mfh.parse


def parse_doc(s: str) -> Doc:
    wiki = parse(s)
    content = NodeBuilder().build_content(wiki)
    return Doc(content)
