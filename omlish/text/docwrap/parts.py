import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang


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
        check.not_empty(self.es)
        for e in self.es:
            check.isinstance(e, Part)


##


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
