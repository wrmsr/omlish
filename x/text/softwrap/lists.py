"""
TODO:
 - improper any children not just sublists?
 - 'inline' (non-indented) lists?
 - numeric lettered lists (even unordered) (with separator - `1)` / `1:` / ...)
"""
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

    class _DetectedList(ta.NamedTuple):
        pfx: str
        ofs: int
        len: int

    def _detect_list(self, ps: ta.Sequence[Part]) -> _DetectedList | None:
        if not ps:
            return None

        if not isinstance(f := ps[0], Text):
            return None

        for lp in self._len_sorted_list_prefixes:
            sp = lp + ' '

            if not f.s.startswith(sp):
                continue

            mo = -1
            n = 0
            while n < len(ps):
                p = ps[n]

                if isinstance(p, (Blank, Text)):
                    if isinstance(p, Text) and not p.s.startswith(sp):
                        break
                    if mo < 0:
                        mo = n

                elif isinstance(p, Indent):
                    if p.n < len(sp):
                        if not self._forbid_improper_sublists and isinstance(p.p, List):
                            continue
                        break

                else:
                    raise TypeError(p)

                n += 1

            if mo >= 0:
                return ListBuilder._DetectedList(lp, mo, n - mo)

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

                st = 0
                while (dl := self._detect_list(new[st:])) is not None:
                    ln = self._build_list(dl.pfx, p.ps[dl.ofs:dl.ofs + dl.len])
                    new[dl.ofs:dl.ofs + dl.len + 1] = [ln]
                    st = dl.ofs + 1

                return blockify(*new)

            elif isinstance(p, Indent):
                if (n := rec(p.p)) is not p.p:
                    p = Indent(p.n, n)  # type: ignore[arg-type]
                return p

            elif isinstance(p, (Blank, Text, List)):
                return p

            else:
                raise TypeError(p)

        return rec(root)
