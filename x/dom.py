"""
TODO:
 - escaping
 - lang.can_import('markupsafe') like http.json

==

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


if ta.TYPE_CHECKING:
    import markupsafe as ms

    _HAS_MARKUPSAFE = True

else:
    ms = lang.proxy_import('markupsafe')

    _HAS_MARKUPSAFE = lang.can_import('markupsafe')


String: ta.TypeAlias = ta.Union[
    str,
    'ms.Markup',
]

Content: ta.TypeAlias = ta.Union[
    list['Content'],
    'Dom',
    String,
    None,
]

ContentT = ta.TypeVar('ContentT', bound=Content)


##


ATTR_NAMES_BY_KWARG: ta.Mapping[str, str] = {
    'class_': 'class',
}

ATTR_KWARGS_BY_NAME: ta.Mapping[str, str] = {v: k for k, v in ATTR_NAMES_BY_KWARG.items()}


def kwargs_to_attrs(**kwargs: ta.Any) -> dict[str, str]:
    return {
        ATTR_NAMES_BY_KWARG.get(k, k).replace('_', '-'): v
        for k, v in kwargs.items()
    }


##


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


def d(
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


STRING_TYPES: tuple[type, ...] = (
    str,
    *([ms.Markup] if _HAS_MARKUPSAFE else []),
)

CONTENT_TYPES: tuple[type, ...] = (
    list,
    Dom,
    *STRING_TYPES,
    type(None),
)


def check_content(c: ContentT) -> ContentT:
    if isinstance(c, list):
        for e in c:
            check_content(e)
    else:
        check.isinstance(c, CONTENT_TYPES)
    return c


def iter_content(c: Content) -> ta.Iterator[Dom | String]:
    if isinstance(c, list):
        for e in c:
            yield from iter_content(e)
    elif isinstance(c, (Dom, *STRING_TYPES)):
        yield c
    elif c is None:
        pass
    else:
        raise TypeError(c)


##


@dc.dataclass(frozen=True)
class DomBuilder:
    tag: str

    def __call__(
            self,
            *attrs_and_contents: tuple[str, ta.Any] | Content,
            **kwargs: ta.Any,
    ) -> Dom:
        return d(self.tag, *attrs_and_contents, **kwargs)


class DomAccessor:
    def __getattr__(self, tag: str) -> DomBuilder:
        return DomBuilder(tag)


D = DomAccessor()


##


@dc.dataclass()
class InvalidTagError(Exception):
    pass


@dc.dataclass()
class StrForbiddenError(Exception):
    pass


class Renderer:
    def __init__(
            self,
            sb: io.StringIO | None,
            *,
            forbid_str: bool = False,
            escape: ta.Callable[[str], str] | None = None,
            indent: str | int | None = None,
    ) -> None:
        super().__init__()

        if sb is None:
            sb = io.StringIO()
        self._sb = sb

        self._forbid_str = forbid_str
        self._escape_fn = escape
        if isinstance(indent, int):
            indent = ' ' * indent
        self._indent_str: str | None = indent

        self._level = 0
        self._indent_cache: dict[int, str] = {}

    def _escape(self, s: str) -> str:
        if _HAS_MARKUPSAFE and isinstance(s, ms.Markup):
            return s
        if type(s) is not str:
            raise TypeError(s)
        if (fn := self._escape_fn) is None:
            return s
        return fn(s)

    def _check_tag(self, s: str) -> str:
        if self._escape(s) != s:
            raise InvalidTagError(s)
        return s

    #

    def _write_indent(self) -> None:
        if not (s := self._indent_str):
            return
        try:
            ls = self._indent_cache[self._level]
        except KeyError:
            ls = self._indent_cache[self._level] = s * self._level
        self._sb.write(ls)

    #

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
        if self._forbid_str:
            raise StrForbiddenError(s)
        self._sb.write(s)

    @render.register  # noqa
    def _render_sequence(self, l: ta.Sequence) -> None:
        for e in l:
            self.render(e)

    #

    if _HAS_MARKUPSAFE:
        @render.register
        def _render_markup(self, m: ms.Markup) -> None:
            self._sb.write(m)

    #

    def _render_tag(self, tag: str) -> None:
        self._sb.write(self._check_tag(tag))

    def _render_attr_key(self, k: str) -> None:
        self._sb.write(self._check_tag(k))

    def _render_attr_value(self, v: ta.Any) -> None:
        self._sb.write('"')
        self._sb.write(check.isinstance(v, str))  # FIXME
        self._sb.write('"')

    @render.register  # noqa
    def _render_dom(self, n: Dom) -> None:
        self._write_indent()

        self._sb.write('<')
        self._render_tag(n.tag)

        for k, v in (n.attrs or {}).items():
            self._sb.write(' ')
            self._render_attr_key(k)
            if v is not None:
                self._sb.write('=')
                self._render_attr_value(v)

        i = -1
        for i, c in enumerate(iter_content(n.body)):
            if not i:
                self._sb.write('>')

            if self._indent_str:
                self._sb.write('\n')

            self._level += 1
            self.render(c)
            self._level -= 1

        if i >= 0:
            if self._indent_str:
                self._sb.write('\n')
                self._write_indent()

            self._sb.write('</')
            self._render_tag(n.tag)
            self._sb.write('>')

        else:
            self._sb.write(' />')


##


def _main() -> None:
    root = d('html').add(
        d('head').add(
            d('title', 'hi'),
        ),
        d('body').add(
            d('svg', id='chart', width='600', height='300'),
            d('div', id='tooltip', class_='tooltip', x_data='{}'),
        ),
    )

    print(root)
    print(Renderer.render_str(root))
    print(Renderer.render_str(root, indent=2))
    print()

    #

    root = D.html(
        D.head(
            D.title('hi'),
        ),
        D.body(
            D.svg(id='chart', width='600', height='300'),
            D.div(id='tooltip', class_='tooltip', x_data='{}'),
        ),
    )

    print(root)
    print(Renderer.render_str(root))
    print(Renderer.render_str(root, indent=2))
    print()

    #

    root = D.html(
        D.head(
            D.script(src="..."),
            D.script(
                "alert('Hello World')"
            ),
        ),
        D.body(
            D.div(
                D.h1(id="title").add("This is a title"),
                D.p("This is a big paragraph of text"),
            ),
        ),
    )

    print(root)
    print(Renderer.render_str(root))
    print(Renderer.render_str(root, indent=2))
    print()


if __name__ == '__main__':
    _main()
