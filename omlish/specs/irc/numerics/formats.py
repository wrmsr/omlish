import dataclasses as dc
import typing as ta

from .... import check
from .... import lang


FormatPart: ta.TypeAlias = ta.Union[str, 'Formats.Optional', 'Formats.Variadic']
FormatParts: ta.TypeAlias = ta.Sequence[FormatPart]


class Formats(lang.Namespace):
    @dc.dataclass(frozen=True)
    class Name:
        name: str

    @dc.dataclass(frozen=True)
    class Optional:
        body: FormatParts

    @dc.dataclass(frozen=True)
    class Variadic:
        body: FormatParts

    #

    _PARTS_BY_DELIMITERS: ta.Mapping[tuple[str, str], type] = {
        ('[', ']'): Optional,
        ('{', '}'): Variadic,
    }

    _DELIMITERS_BY_PARTS: ta.Mapping[type, tuple[str, str]] = {v: k for k, v in _PARTS_BY_DELIMITERS.items()}

    #

    @staticmethod
    def split_parts(s: str) -> FormatParts:
        stk: list[tuple[str, list]] = [('', [])]

        p = 0
        while p < len(s):
            n = lang.find_any(s, '{}[]<', p)

            if n < 0:
                check.state(not stk[-1][0])
                stk[-1][1].append(s[p:])
                break

            if n != p:
                stk[-1][1].append(s[p:n])

            d = s[n]
            if d == '<':
                e = s.index('>', n)
                stk[-1][1].append(Formats.Name(s[n + 1:e]))
                p = e + 1

            elif d in '{[':
                stk.append((d, []))
                p = n + 1

            elif d in '}]':
                x, l = stk.pop()
                pc = Formats._PARTS_BY_DELIMITERS[(x, d)]
                stk[-1][1].append(pc(l))
                p = n + 1

            else:
                raise RuntimeError

        _, ret = check.single(stk)
        return ret

    #

    @staticmethod
    def render_parts(p: FormatPart | FormatParts) -> ta.Iterator[str]:
        if isinstance(p, str):
            yield p

        elif isinstance(p, Formats.Name):
            yield '<'
            yield p.name
            yield '>'

        elif isinstance(p, (Formats.Optional, Formats.Variadic)):
            l, r = Formats._DELIMITERS_BY_PARTS[type(p)]
            yield l
            yield from Formats.render_parts(p.body)
            yield r

        else:
            for c in p:
                yield from Formats.render_parts(c)
