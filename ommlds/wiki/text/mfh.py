"""
TODO:
 - Argument

https://mwparserfromhell.readthedocs.io/en/latest/api/mwparserfromhell.nodes.html#module-mwparserfromhell.nodes
"""
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


with lang.auto_proxy_import(globals()):
    import mwparserfromhell as mfh
    import mwparserfromhell.nodes as mfn


Wikicode: ta.TypeAlias = 'mfh.wikicode.Wikicode'


##


@dc.dataclass(frozen=True)
class Node(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class ContentNode(Node, lang.Abstract):
    pass


Content: ta.TypeAlias = ta.Sequence[ContentNode]


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['body'], omit_if=operator.not_)
class Doc(Node):
    body: Content = ()


@dc.dataclass(frozen=True)
class Text(ContentNode):
    s: str


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['title', 'text'], omit_if=operator.not_)
class WikiLink(ContentNode):
    title: Content = ()
    text: Content = ()


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['title', 'url'], omit_if=operator.not_)
class ExternalLink(ContentNode):
    title: Content = ()
    url: Content = ()


@dc.dataclass(frozen=True)
class Html(ContentNode):
    s: str


@dc.dataclass(frozen=True)
class Comment(ContentNode):
    s: str


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['name', 'value'], omit_if=operator.not_)
class Parameter(Node):
    name: Content = ()
    value: Content = ()


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['name', 'params'], omit_if=operator.not_)
class Template(ContentNode):
    name: Content = ()
    params: ta.Sequence[Parameter] = ()


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['name', 'value'], omit_if=operator.not_)
class Attribute(Node):
    name: Content = ()
    value: Content = ()


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['l', 'atts', 'body', 'r'], omit_if=operator.not_)
class Tag(ContentNode):
    l: Content = ()
    atts: ta.Sequence[Attribute] = ()
    body: Content = ()
    r: Content = ()


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['title'], omit_if=operator.not_)
class Heading(ContentNode):
    title: Content = ()
    level: int = 0


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['name', 'default'], omit_if=operator.not_)
class Argument(ContentNode):
    name: Content = ()
    default: Content = ()


##


def _install_msh_poly(cls: type) -> None:
    p = msh.polymorphism_from_subclasses(cls, naming=msh.Naming.SNAKE)
    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(p),
        msh.PolymorphismUnmarshalerFactory(p),
    )


_install_msh_poly(Node)
_install_msh_poly(ContentNode)


##


def one_text(nodes: Content) -> str | None:
    if len(nodes) == 1 and isinstance(n := nodes[0], Text):
        return n.s
    return None


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
    def build_parameter(self, n: 'mfn.extras.Parameter') -> Parameter:
        if not isinstance(n, mfn.extras.Parameter):
            raise TypeError(n)

        return Parameter(
            self.build_content(n.name),
            self.build_content(n.value),
        )

    def build_attribute(self, n: 'mfn.extras.Attribute') -> Attribute:
        if not isinstance(n, mfn.extras.Attribute):
            raise TypeError(n)

        return Attribute(
            self.build_content(n.name),
            self.build_content(n.value),
        )

    def build_content_node(self, n: 'mfn.Node') -> ContentNode:
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

    def build_content(self, w: Wikicode | ta.Iterable['mfn.Node'] | None) -> Content:
        if w is None:
            return ()

        elif isinstance(w, mfh.wikicode.Wikicode):
            return [self.build_content_node(c) for c in w.nodes]

        elif isinstance(w, ta.Iterable):
            return [self.build_content_node(check.isinstance(c, mfn.Node)) for c in w]

        else:
            raise TypeError(w)


##


def parse(
        value: ta.Any,
        context: int = 0,
        *,
        skip_style_tags: bool = False,
        **kwargs: ta.Any,
) -> Wikicode:
    return mfh.parse(
        value,
        context,
        skip_style_tags=skip_style_tags,
        **kwargs,
    )


def parse_doc(s: str) -> Doc:
    wiki = parse(s)
    content = NodeBuilder().build_content(wiki)
    return Doc(content)
