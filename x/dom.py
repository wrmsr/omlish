"""
https://github.com/bloodearnest/hdom
html = h.div(h.p("Hello"), h.table(h.tr(h.td("foo"), h.td("bar"))))

https://github.com/Knio/dominate
doc = html()
with doc:
    with body():
        h = h1('Title')
        t = table()
        with t:
            with tr():
                td('foo')
                td('bar')

https://www.yattag.org/
doc, tag, text = Doc().tagtext()
with tag('table'):
    with tag('tr'):
        with tag('td'):
            text('foo')
        with tag('td'):
            text('bar')

Hyperscript / Snabbdom-style JSX alternatives] (JavaScript)
h('table', {}, [
  h('tr', {}, [
    h('td', {}, 'foo'),
    h('td', {}, 'bar')
  ])
])

https://github.com/com-lihaoyi/scalatags
val htmlFrag = table(
  tr(
    td("foo"), td("bar")
  )
)

Elm's Html DSL (Elm)
table []
  [ tr []
      [ td [] [ text "foo" ]
      , td [] [ text "bar" ]
      ]
  ]

Fluent API Style
html = node.html().body().p("Hello").table().tr().td("foo").td("bar")

Attributes & Text
node.div(id="main", cls="container").p("Hello")
"""
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang


Content: ta.TypeAlias = ta.Union[
    list['Content'],
    'Dom',
    str,
    None,
]

ContentT = ta.TypeVar('ContentT', bound=Content)


##


ATTR_NAMES_BY_KWARG: ta.Mapping[str, str] = {
    'class_': 'class',
}

ATTR_KWARGS_BY_NAME: ta.Mapping[str, str] = {v: k for k, v in ATTR_NAMES_BY_KWARG.items()}


def kwargs_to_attrs(**kwargs: ta.Any) -> dict[str, str]:
    return {ATTR_NAMES_BY_KWARG.get(k, k): v for k, v in kwargs.items()}


@dc.dataclass()
class Dom:
    tag: str
    attrs: dict[str, ta.Any | None] | None = dc.xfield(None, repr_fn=lang.opt_repr)
    body: list[Content] = dc.xfield(None, repr_fn=lang.opt_repr)

    def set(self, **kwargs: ta.Any) -> 'Dom':
        if self.attrs is None:
            self.attrs = {}
        self.attrs.update(**kwargs_to_attrs(**kwargs))
        return self

    def unset(self, *keys: str) -> 'Dom':
        if self.attrs is not None:
            for k in keys:
                self.attrs.pop(k, None)
        return self

    def add(self, *contents: Content) -> 'Dom':
        if self.body is None:
            self.body = []
        for c in contents:
            check_content(c)
        self.body.extend(contents)
        return self

    def remove(self, *contents: Content, strict: bool = False) -> 'Dom':
        if self.body is not None:
            i = 0
            while i < len(self.body):
                e = self.body[i]
                if any(c is e for c in contents):
                    del self.body[i]
                elif strict:
                    raise ValueError(f'Content {e} not in body')
                else:
                    i += 1
        return self


##


def dom(
        tag: str,
        *attrs_and_contents: tuple[str, ta.Any] | Content,
        **kwargs: ta.Any,
) -> Dom:
    c = []
    for a in attrs_and_contents:
        if isinstance(a, tuple):
            k, v = a
            if k in kwargs:
                raise KeyError(f'Attribute {k} already set')
            kwargs[k] = v
        else:
            c.append(a)

    return Dom(
        tag,
        attrs=kwargs_to_attrs(**kwargs) or None,
        body=c or None,
    )


##


CONTENT_TYPES: tuple[type, ...] = (
    list,
    Dom,
    str,
    type(None),
)


def check_content(c: ContentT) -> ContentT:
    if isinstance(c, list):
        for e in c:
            check_content(e)
    else:
        check.isinstance(c, CONTENT_TYPES)
    return c


##


@dc.dataclass(frozen=True)
class DomBuilder:
    tag: str

    def __call__(
            self,
            *attrs_and_contents: tuple[str, ta.Any] | Content,
            **kwargs: ta.Any,
    ) -> Dom:
        return dom(self.tag, *attrs_and_contents, **kwargs)


class DomAccessor:
    def __getattr__(self, tag: str) -> DomBuilder:
        return DomBuilder(tag)


D = DomAccessor()


##


class Renderer:
    def __init__(self, sb: io.StringIO | None) -> None:
        super().__init__()

        if sb is None:
            sb = io.StringIO()
        self._sb = sb

    @dispatch.method
    def render(self, o: ta.Any) -> None:
        raise TypeError(o)

    @classmethod
    def render_str(cls, o: ta.Any, **kwargs: ta.Any) -> str:
        sb = io.StringIO()
        cls(sb, **kwargs).render(o)
        return sb.getvalue()

    #

    @render.register  # noqa
    def _render_str(self, s: str) -> None:
        self._sb.write(s)

    @render.register  # noqa
    def _render_seq(self, l: ta.Sequence) -> None:
        for e in l:
            self.render(e)

    #

    def _render_tag(self, tag: str) -> None:
        self._sb.write(tag)

    def _render_attr_key(self, k: str) -> None:
        self._sb.write(k)

    def _render_attr_value(self, v: ta.Any) -> None:
        self._sb.write(f'"{check.isinstance(v, str)}"')

    @render.register  # noqa
    def _render_dom(self, n: Dom) -> None:
        self._sb.write('<')
        self._render_tag(n.tag)

        for k, v in (n.attrs or {}).items():
            self._sb.write(' ')
            self._render_attr_key(k)
            if v is not None:
                self._sb.write('=')
                self._render_attr_value(v)

        if n.body is not None:
            self._sb.write('>')
            self.render(n.body)
            self._sb.write('</')
            self._render_tag(n.tag)
            self._sb.write('>')

        else:
            self._sb.write(' />')


##


def _main() -> None:
    root = dom('html').add(
        dom('head').add(
            dom('title', 'hi'),
        ),
        dom('body').add(
            dom('svg', id='chart', width='600', height='300'),
            dom('div', id='tooltip', class_='tooltip')
        ),
    )

    print(root)
    print(Renderer.render_str(root))

    root = D.html(
        D.head(
            D.title('hi'),
        ),
        D.body(
            D.svg(id='chart', width='600', height='300'),
            D.div(id='tooltip', class_='tooltip'),
        ),
    )

    print(root)
    print(Renderer.render_str(root))


if __name__ == '__main__':
    _main()
