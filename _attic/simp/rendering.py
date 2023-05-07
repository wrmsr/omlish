"""
TODO:
 - parens, lols
"""
import typing as ta

from . import nodes as no
from .. import check
from .. import dispatch
from ..code import rendering as r


def needs_paren(node: no.Node) -> bool:
    return False


class Renderer(dispatch.Class):
    render = dispatch.property()

    def __call__(self, node: ta.Optional[no.Node]) -> r.Part:
        if node is None:
            return []
        return [r.Node(node), self.render(node)]

    def render(self, node: no.Node) -> r.Part:  # noqa
        raise TypeError(node)

    def paren(self, node: no.Node) -> r.Part:  # noqa
        return r.Wrap(self(node)) if needs_paren(node) else self(node)

    def render(self, node: no.Arg) -> r.Part:  # noqa
        if node.default is not None:
            default = ['=', self.render(node.default)]
        else:
            default = []
        if node.annotation is not None:
            return [r.Concat([self.render(node.name), ':']), self.render(node.annotation), *default]
        else:
            return r.Concat([self.render(node.name), *default])

    def render(self, node: no.Args) -> r.Part:  # noqa
        l = []  # noqa
        l.extend(self.render(a) for a in node.args)
        if node.vararg:
            l.append(r.Concat(['*', self.render(node.vararg)]))
        elif node.kwonly_args:
            l.append('*')
        if node.kwonly_args:
            l.extend(self.render(a) for a in node.kwonly_args)
        if node.kwarg is not None:
            l.append(r.Concat(['**', self.render(node.kwarg)]))
        return r.List(l)

    def render(self, node: no.BinExpr) -> r.Part:  # noqa
        return [self.paren(node.left), self.render(node.op), self.paren(node.right)]

    def render(self, node: no.BoolExpr) -> r.Part:  # noqa
        return [self.paren(node.left), self.render(node.op), self.paren(node.right)]

    def render(self, node: no.Break) -> r.Part:  # noqa
        return 'break'

    def render(self, node: no.Call) -> r.Part:  # noqa
        return r.Concat([
            self.render(node.fn),
            r.Wrap(r.List([self.render(a) for a in [*node.args, *node.keywords]])),
        ])

    def render(self, node: no.CmpExpr) -> r.Part:  # noqa
        return [self.paren(node.left), self.render(node.op), self.paren(node.right)]

    def render(self, node: no.Const) -> r.Part:  # noqa
        return repr(node.value)

    def render(self, node: no.Continue) -> r.Part:  # noqa
        return 'continue'

    def render(self, node: no.ExprStmt) -> r.Part:  # noqa
        return self.render(node.expr)

    def render(self, node: no.Fn) -> r.Part:  # noqa
        args = [self.render(node.name), r.Wrap(self.render(node.args))]
        if node.annotation is not None:
            proto = [r.Concat(args), '->', r.Concat([self.render(node.annotation), ':'])]
        else:
            proto = r.Concat([*args, ':'])

        return r.Block([
            ['def', proto],
            r.Section([
                r.Block([self.render(d) for d in node.body]),
            ]),
        ])

    def render(self, node: no.ForIter) -> r.Part:  # noqa
        return r.Block([
            ['for', self.render(node.var), 'in', r.Concat([self.render(node.iter), ':'])],
            r.Section([r.Block([self.render(s) for s in node.body])]),
        ])

    def render(self, node: no.GetAttr) -> r.Part:  # noqa
        return r.Concat([self.render(node.obj), '.', self.render(node.attr)])

    def render(self, node: no.GetItem) -> r.Part:  # noqa
        return r.Concat([self.render(node.obj), r.Wrap(self.render(node.idx), ('[', ']'))])

    def render(self, node: no.GetVar) -> r.Part:  # noqa
        return self.render(node.name)

    def render(self, node: no.Ident) -> r.Part:  # noqa
        return node.s

    def render(self, node: no.If) -> r.Part:  # noqa
        return r.Block([
            ['if', r.Concat([self.render(node.test), ':'])],
            r.Section([r.Block([self.render(s) for s in node.then])]),
            *([
                r.Concat(['else', ':']),
                r.Section([r.Block([self.render(s) for s in node.else_])])
            ] if node.else_ else []),
        ])

    def render(self, node: no.Keyword) -> r.Part:  # noqa
        if node.name is not None:
            return r.Concat([self.render(node.name), '=', self(node.value)])
        else:
            return r.Concat(['**', self(node.value)])

    def render(self, node: no.Pass) -> r.Part:  # noqa
        return 'pass'

    def render(self, node: no.Module) -> r.Part:  # noqa
        return [self.render(d) for d in node.defs]

    def render(self, node: no.Op) -> r.Part:  # noqa
        return node.glyph_parts

    def render(self, node: no.Raise) -> r.Part:  # noqa
        return ['raise', [self.render(node.value)] if node.value is not None else []]

    def render(self, node: no.Return) -> r.Part:  # noqa
        return ['return', [self.render(node.value)] if node.value is not None else []]

    def render(self, node: no.SetAttr) -> r.Part:  # noqa
        return [
            r.Concat([
                self.render(node.obj),
                '.',
                self.render(node.attr),
                *([':'] if node.annotation is not None else []),
            ]),
            [self.render(node.annotation)] if node.annotation is not None else [],
            '=',
            self.render(node.value),
        ]

    def render(self, node: no.SetItem) -> r.Part:  # noqa
        return [
            r.Concat([
                self.render(node.obj),
                r.Wrap(self.render(node.idx), ('[', ']')),
                *([':'] if node.annotation is not None else []),
            ]),
            [self.render(node.annotation)] if node.annotation is not None else [],
            '=',
            self.render(node.value),
        ]

    def render(self, node: no.SetVar) -> r.Part:  # noqa
        return [
            r.Concat([self.render(node.name), *([':'] if node.annotation is not None else [])]),
            [self.render(node.annotation)] if node.annotation is not None else [],
            '=',
            self.render(node.value),
        ]

    def render(self, node: no.Starred) -> r.Part:  # noqa
        return r.Concat(['*', self.render(node.value)])

    def render(self, node: no.UnaryExpr) -> r.Part:  # noqa
        if node.op.is_word:
            return [*node.op.glyph_parts, self.paren(node.value)]
        else:
            return r.Concat([node.op.glyph, self.paren(node.value)])


def render(node: no.Node) -> str:
    check.isinstance(node, no.Node)
    part = Renderer()(node)
    part = r.remove_nodes(part)
    part = r.compact_part(part)
    return r.render_part(part).getvalue()
