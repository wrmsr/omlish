import typing as ta

from omlish import check

from .parts import Blank
from .parts import Block
from .parts import Indent
from .parts import List
from .parts import Part
from .parts import Text
from .parts import blockify
from .utils import all_same


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

        new: list[list[Part]] = []

        f = check.isinstance(ps[0], Text)
        check.state(f.s.startswith(sp))
        new.append([Text(f.s[len(sp):])])
        del f

        for i in range(1, len(ps)):
            p = ps[i]

            if isinstance(p, Blank):
                new[-1].append(p)

            elif isinstance(p, Text):
                check.state(p.s.startswith(sp))
                new.append([Text(p.s[len(sp):])])

            elif isinstance(p, Indent):
                if (
                        p.n < len(sp) and
                        isinstance(p.p, List) and
                        not self._forbid_improper_sublists
                ):
                    # Promote improper sublists to the outer list's indent
                    p = Indent(len(sp), p.p)

                if p.n == len(sp):
                    new[-1].append(p.p)

                else:
                    raise NotImplementedError

            else:
                raise TypeError(p)

        #

        return List(lp, [blockify(*x) for x in new])

    def build_lists(self, root: Part) -> Part:
        def rec(p: Part) -> Part:  # noqa
            if isinstance(p, Block):
                new = [rec(c) for c in p.ps]
                if not all_same(new, p.ps):
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
