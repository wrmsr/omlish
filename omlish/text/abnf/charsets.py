# ruff: noqa: SLF001
"""
immutable sets of unicode codepoints, stored as normalized interval lists. This is the char-class algebra the
FIRST/FOLLOW analysis computes over.

(Not an interval *tree* -- trees answer stabbing queries over overlapping interval collections; here intervals are
disjoint and normalized, and the workhorse ops are set-algebraic merges, which are O(n + m) two-pointer walks over
sorted tuples.)

Representation invariant: `_ivs` is a tuple of (lo, hi) inclusive codepoint pairs, sorted, non-overlapping, non-adjacent
(hi + 1 < next lo). Normalization at construction makes __eq__/__hash__ structural, which the fixpoint solvers rely on.
"""
import typing as ta


##


class CharSet:
    __slots__ = ('_ivs',)

    def __init__(self, ivs: ta.Iterable[tuple[int, int]] = ()) -> None:
        super().__init__()

        # normalize: sort, drop empties, merge overlapping/adjacent
        out: list[tuple[int, int]] = []
        for lo, hi in sorted(ivs):
            if hi < lo:
                continue
            if out and lo <= out[-1][1] + 1:
                if hi > out[-1][1]:
                    out[-1] = (out[-1][0], hi)
            else:
                out.append((lo, hi))
        self._ivs: tuple[tuple[int, int], ...] = tuple(out)

    #

    EMPTY: ta.ClassVar[CharSet]
    ANY: ta.ClassVar[CharSet]

    @classmethod
    def of_chars(cls, s: ta.Iterable[str]) -> CharSet:
        return cls((ord(c), ord(c)) for c in s)

    @classmethod
    def of_range(cls, lo: str, hi: str) -> CharSet:
        return cls(((ord(lo), ord(hi)),))

    def fold_case(self) -> CharSet:
        """
        Closure under simple (length-preserving, char-by-char) case mappings -- matching what a per-char
        case-insensitive comparison can accept. Multi-char foldings ('ß' -> 'ss') are intentionally out of scope; see
        the CI-literal caveats in opto.
        """

        cs: set[int] = set()
        for lo, hi in self._ivs:
            for cp in range(lo, hi + 1):
                c = chr(cp)
                for v in (c, c.lower(), c.upper(), c.casefold()):
                    if len(v) == 1:
                        cs.add(ord(v))
        return CharSet((c, c) for c in cs)

    #

    def __or__(self, other: CharSet) -> CharSet:
        return CharSet((*self._ivs, *other._ivs))

    def __and__(self, other: CharSet) -> CharSet:
        out: list[tuple[int, int]] = []
        a, b, i, j = self._ivs, other._ivs, 0, 0
        while i < len(a) and j < len(b):
            lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
            if lo <= hi:
                out.append((lo, hi))
            if a[i][1] < b[j][1]:
                i += 1
            else:
                j += 1
        return CharSet(out)

    def __sub__(self, other: CharSet) -> CharSet:
        out: list[tuple[int, int]] = []
        j = 0
        for lo, hi in self._ivs:
            cur = lo
            while j < len(other._ivs) and other._ivs[j][1] < cur:
                j += 1
            k = j
            while k < len(other._ivs) and other._ivs[k][0] <= hi:
                blo, bhi = other._ivs[k]
                if blo > cur:
                    out.append((cur, blo - 1))
                cur = max(cur, bhi + 1)
                if cur > hi:
                    break
                k += 1
            if cur <= hi:
                out.append((cur, hi))
        return CharSet(out)

    def isdisjoint(self, other: CharSet) -> bool:
        a, b, i, j = self._ivs, other._ivs, 0, 0
        while i < len(a) and j < len(b):
            if a[i][1] < b[j][0]:
                i += 1
            elif b[j][1] < a[i][0]:
                j += 1
            else:
                return False
        return True

    #

    def __contains__(self, c: str) -> bool:
        cp = ord(c)
        # bisect would be fine; sets here are tiny
        return any(lo <= cp <= hi for lo, hi in self._ivs)

    def __bool__(self) -> bool:
        return bool(self._ivs)

    def __len__(self) -> int:
        return sum(hi - lo + 1 for lo, hi in self._ivs)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CharSet) and self._ivs == other._ivs

    def __hash__(self) -> int:
        return hash((self.__class__, self._ivs))

    def __repr__(self) -> str:
        def part(lo: int, hi: int) -> str:
            if lo == hi:
                return f'{chr(lo)!r}'
            return f'{chr(lo)!r}-{chr(hi)!r}'
        return f'CharSet({{{", ".join(part(lo, hi) for lo, hi in self._ivs)}}})'

    @property
    def intervals(self) -> tuple[tuple[int, int], ...]:
        return self._ivs


CharSet.EMPTY = CharSet()
CharSet.ANY = CharSet(((0, 0x10FFFF),))
