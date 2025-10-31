"""
TODO:
 - do we support lists of one item? we should
"""
import functools
import io
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Part(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Text(Part, lang.Final):
    s: str

    @dc.init
    def _check_s(self) -> None:
        check.non_empty_str(self.s)
        check.state(self.s == self.s.strip())


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Blank(Part, lang.Final):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Indent(Part, lang.Final):
    n: int = dc.xfield(validate=lambda n: n > 0)
    p: ta.Union[Text, 'Block', 'List'] = dc.xfield(coerce=lambda p: check.isinstance(p, (Text, Block, List)))


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class Block(Part, lang.Final):
    ps: ta.Sequence[Part]

    @dc.init
    def _check_ps(self) -> None:
        check.state(len(self.ps) > 1)
        for i, p in enumerate(self.ps):
            check.isinstance(p, Part)
            if i and isinstance(p, Block):
                check.not_isinstance(self.ps[i - 1], Block)


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class List(Part, lang.Final):
    d: str = dc.xfield(coerce=check.non_empty_str)
    es: ta.Sequence[Part] = dc.xfield()

    @dc.init
    def _check_es(self) -> None:
        check.state(len(self.es) > 1)
        for e in self.es:
            check.isinstance(e, Part)


#


def _all_same(l: ta.Sequence[T], r: ta.Sequence[T]) -> bool:
    return len(l) == len(r) and all(x is y for x, y in zip(l, r, strict=True))


def _squish(ps: ta.Sequence[Part]) -> ta.Sequence[Part]:
    for p in ps:
        check.isinstance(p, Part)

    if len(ps) < 2:
        return ps

    while True:
        if any(isinstance(p, Block) for p in ps):
            ps = list(lang.flatmap(lambda p: p.ps if isinstance(p, Block) else [p], ps))
            continue

        if any(
                isinstance(ps[i], Indent) and
                isinstance(ps[i + 1], Indent) and
                ps[i].n == ps[i + 1].n  # type: ignore[attr-defined]
                for i in range(len(ps) - 1)
        ):
            new: list[Part | tuple[int, list[Part]]] = []
            for p in ps:
                if isinstance(p, Indent):
                    if new and isinstance(y := new[-1], tuple) and p.n == y[0]:
                        y[1].append(p.p)
                    else:
                        new.append((p.n, [p.p]))
                else:
                    new.append(p)
            ps = [
                Indent(x[0], blockify(*x[1])) if isinstance(x, tuple) else x  # type: ignore[arg-type]
                for x in new
            ]
            continue

        break

    return ps


def blockify(*ps: Part) -> Part:
    check.not_empty(ps)
    ps = _squish(ps)  # type: ignore[assignment]
    if len(ps) == 1:
        return ps[0]
    return Block(ps)


##


DEFAULT_TAB_WIDTH: int = 4


def replace_tabs(s: str, tab_width: int = DEFAULT_TAB_WIDTH) -> str:
    return s.replace('\t', ' ' * tab_width)


##


def build_root(s: str) -> Part:
    lst: list[Part] = []

    for l in s.splitlines():
        if not (sl := l.strip()):
            lst.append(Blank())
            continue

        p: Part = Text(sl)

        n = next((i for i, c in enumerate(l) if not c.isspace()), 0)
        if n:
            p = Indent(n, p)  # type: ignore[arg-type]

        lst.append(p)

    if len(lst) == 1:
        return lst[0]
    else:
        return Block(lst)


##


@dc.dataclass()
@dc.extra_class_params(default_repr_fn=dc.truthy_repr)
class _IndentGroup:
    n: int
    cs: list[ta.Union[Blank, Text, '_IndentGroup']] = dc.field(default_factory=list)


def group_indents(root: Part) -> Part:
    rg = _IndentGroup(0)
    stk: list[_IndentGroup] = [rg]

    for p in (root.ps if isinstance(root, Block) else [root]):
        if isinstance(p, Blank):
            stk[-1].cs.append(p)
            continue

        n: int
        t: Text
        if isinstance(p, Text):
            n, t = 0, p
        elif isinstance(p, Indent):
            n = p.n
            t = check.isinstance(p.p, Text)
        else:
            raise TypeError(p)

        while n < stk[-1].n:
            stk.pop()

        if n > stk[-1].n:
            nxt = _IndentGroup(n=n, cs=[t])
            stk[-1].cs.append(nxt)
            stk.append(nxt)

        else:
            check.state(stk[-1].n == n)
            stk[-1].cs.append(t)

    #

    def relativize(g: '_IndentGroup') -> None:
        for c in g.cs:
            if isinstance(c, _IndentGroup):
                check.state(c.n > g.n)
                relativize(c)
                c.n -= g.n

    relativize(rg)

    #

    def convert(g: '_IndentGroup') -> Part:
        if g.n < 1:
            check.state(g is rg)

        lst: list[Part] = []
        for c in g.cs:
            if isinstance(c, (Blank, Text)):
                lst.append(c)

            elif isinstance(c, _IndentGroup):
                lst.append(Indent(c.n, convert(c)))  # type: ignore[arg-type]

            else:
                raise TypeError(c)

        return blockify(*lst)

    return convert(rg)


##


class ListBuilder:
    DEFAULT_LIST_PREFIXES: ta.ClassVar[ta.Sequence[str]] = ['*', '-']

    def __init__(
            self,
            *,
            list_prefixes: ta.Iterable[str] | None = None,
            forbid_improper_sublists: bool = False,
    ) -> None:
        super().__init__()

        if list_prefixes is None:
            list_prefixes = self.DEFAULT_LIST_PREFIXES
        self._list_prefixes = set(check.not_isinstance(list_prefixes, str))
        self._forbid_improper_sublists = forbid_improper_sublists

        self._len_sorted_list_prefixes = sorted(self._list_prefixes, key=len, reverse=True)

    #

    def _detect_list_prefix(self, ps: ta.Sequence[Part]) -> str | None:
        check.not_empty(ps)

        if not isinstance(f := ps[0], Text):
            return None

        for lp in self._len_sorted_list_prefixes:
            sp = lp + ' '

            if not f.s.startswith(sp):
                continue

            i = 0
            for p in ps:
                if isinstance(p, (Blank, Text)):
                    if isinstance(p, Text) and not p.s.startswith(sp):
                        break
                    i += 1
                    continue

                elif isinstance(p, Indent):
                    if p.n < len(sp):
                        if not self._forbid_improper_sublists and isinstance(p.p, List):
                            continue

                        break

                else:
                    raise TypeError(p)

            else:
                if i:
                    return lp

        return None

    def _build_list(self, lp: str, ps: ta.Sequence[Part]) -> List:
        sp = lp + ' '

        new: list[Part | list[Part]] = []

        f = check.isinstance(ps[0], Text)
        check.state(f.s.startswith(sp))
        new.append(Text(f.s[len(sp):]))
        del f

        for i in range(1, len(ps)):
            p = ps[i]

            if isinstance(p, Blank):
                new.append(p)

            elif isinstance(p, Text):
                check.state(p.s.startswith(sp))
                new.append(Text(p.s[len(sp):]))

            elif isinstance(p, Indent):
                if (
                        p.n < len(sp) and
                        isinstance(p.p, List) and
                        not self._forbid_improper_sublists
                ):
                    # Promote improper sublists to the outer list's indent
                    p = Indent(len(sp), p.p)

                if p.n == len(sp):
                    x = new[-1]
                    if not isinstance(x, list):
                        x = [x]
                        new[-1] = x
                    x.append(p.p)

                else:
                    raise NotImplementedError

            else:
                raise TypeError(p)

        #

        return List(lp, [
            blockify(*x) if isinstance(x, list) else x
            for x in new
        ])

    def build_lists(self, root: Part) -> Part:
        def rec(p: Part) -> Part:  # noqa
            if isinstance(p, Block):
                new = [rec(c) for c in p.ps]
                if not _all_same(new, p.ps):
                    return rec(blockify(*new))

                if (lp := self._detect_list_prefix(p.ps)) is None:
                    return p

                return self._build_list(lp, p.ps)

            elif isinstance(p, Indent):
                if (n := rec(p.p)) is not p.p:
                    p = Indent(p.n, n)  # type: ignore[arg-type]
                return p

            elif isinstance(p, (Blank, Text, List)):
                return p

            else:
                raise TypeError(p)

        return rec(root)


##


def join_text(lst: ta.Sequence[str], ci: int = 0) -> ta.Sequence[str]:
    # TODO:
    #  - detect if 'intentionally' smaller than current remaining line width, if so do not merge.
    #  - maybe if only ending with punctuation?
    return [' '.join(lst)]


class TextJoiner(ta.Protocol):
    def __call__(self, strs: ta.Sequence[str], current_indent: int) -> ta.Sequence[str]: ...


def join_block_text(
        root: Part,
        text_joiner: TextJoiner = join_text,
) -> Part:
    def rec(p: Part, ci: int) -> Part:
        if isinstance(p, (Blank, Text)):
            return p

        elif isinstance(p, Indent):
            if (np := rec(p.p, ci + p.n)) is not p.p:
                p = Indent(p.n, np)  # type: ignore[arg-type]
            return p

        elif isinstance(p, List):
            ne = [rec(e, ci + len(p.d) + 1) for e in p.es]
            if not _all_same(ne, p.es):
                p = List(p.d, ne)
            return p

        elif not isinstance(p, Block):
            raise TypeError(p)

        ps = [rec(c, ci) for c in p.ps]

        if not any(
            isinstance(ps[i], Text) and
            isinstance(ps[i + 1], Text)
            for i in range(len(ps) - 1)
        ):
            if not _all_same(ps, p.ps):
                p = blockify(*ps)
            return p

        new: list[Part | list[str]] = []
        for c in ps:
            if isinstance(c, Text):
                if new and isinstance(x := new[-1], list):
                    x.append(c.s)
                else:
                    new.append([c.s])
            else:
                new.append(c)

        return blockify(*lang.flatmap(
            lambda x: map(Text, join_text(x, ci)) if isinstance(x, list) else [x],  # noqa
            new
        ))

    return rec(root, 0)

##


def chop(s: str) -> Part:
    s = replace_tabs(s)

    root = build_root(s)
    root = group_indents(root)
    root = ListBuilder().build_lists(root)
    root = join_block_text(root)

    return root


##


@functools.lru_cache()
def _indent_str(n: int) -> str:
    return ' ' * n


def render_part_to(root: Part, out: ta.Callable[[str], ta.Any]) -> None:
    i_stk: list[int] = [0]
    ci = 0

    def write(s: str, ti: int | None = None) -> None:
        if (nl := '\n' in s) and s != '\n':
            check.state(s[-1] == '\n')
            check.state(s.count('\n') == 1)

        if ti is None:
            ti = i_stk[-1]
        nonlocal ci
        if ci < ti:
            out(_indent_str(ti - ci))
            ci = ti

        out(s)

        if nl:
            ci = 0

    def rec(p: Part) -> None:
        nonlocal ci

        if isinstance(p, Blank):
            check.state(ci == 0)
            out('\n')

        elif isinstance(p, Text):
            write(p.s)
            write('\n')

        elif isinstance(p, Block):
            for c in p.ps:
                rec(c)

        elif isinstance(p, Indent):
            i_stk.append(i_stk[-1] + p.n)
            rec(p.p)
            i_stk.pop()

        elif isinstance(p, List):
            i_stk.append((li := i_stk[-1]) + len(p.d) + 1)
            sd = p.d + ' '
            for e in p.es:
                if isinstance(e, Blank):
                    rec(e)
                else:
                    check.state(ci == 0)
                    write(sd, li)
                    ci += len(sd)
                    rec(e)
            i_stk.pop()

        else:
            raise TypeError(p)

    rec(root)
    check.state(i_stk == [0])


def render_part(root: Part) -> str:
    buf = io.StringIO()
    render_part_to(root, buf.write)
    return buf.getvalue()


##


def _main() -> None:
    print()

    #

    print(blockify(
        Text('hi'),
        Block([Text('foo'), Text('foo2')]),
        Block([Text('bar'), Text('bar2')]),
    ))
    print(blockify(
        Text('hi'),
        Indent(2, Text('a')),
        Indent(2, Text('b')),
    ))
    print()

    #

    root = chop("""\
    Hi I'm some text.
    
    I am more text.
    
    This is a list:
     - Item one
     - item 2
       with another line
    
     - here is a proper nested list
       - subitem 1
         with a second line
       - subitem 2
       
       - subitem 3
    
     - here is an improper nested list
      - subitem 1
        with a second line
        and a third
      - subitem 2
      
      - subitem 3
     
     - item last

  the fuck?
""")
    print(root)
    print(render_part(root))
    print()

    #

    # from omlish.formats import json
    # from omlish import marshal as msh
    #
    # msh.install_standard_factories(
    #     *msh.standard_polymorphism_factories(part_poly := msh.polymorphism_from_subclasses(Part)),
    #     msh.PolymorphismUnionMarshalerFactory(part_poly.impls, allow_partial=True),
    # )
    #
    # print(json.dumps_pretty(msh.marshal(root, Part)))
    # print()


if __name__ == '__main__':
    _main()
