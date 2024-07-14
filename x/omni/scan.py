"""
TODO:
 - (s)re.py? ..
 - match/search/findall
 - numbers (decimal)
 - datetimes
 - {a.b} -> {'a': {'b': ...}}
"""
import io
import re
import sre_constants as srn
import sre_compile as srm
import sre_parse as srp
import typing as ta

from . import dataclasses as dc
from . import check
from . import lang


lang.warn_unstable()


T = ta.TypeVar('T')
Converter = ta.Callable[[str, ta.Sequence[str]], T]


class SpecStr(ta.NamedTuple):
    s: str


class Spec(dc.Pure):
    s: str = dc.field(check_type=str)
    name: ta.Optional[str] = dc.field(None, check_type=(str, None), check=lambda s: s is None or s)
    align: ta.Optional[str] = dc.field(None, kwonly=True)
    inv_case: bool = dc.field(False, kwonly=True)
    optional: bool = dc.field(False, kwonly=True)


class Pat(dc.Pure):
    s: str = dc.field(check_type=str)
    converter: ta.Optional[Converter] = None
    type: ta.Optional[ta.Type] = None


class SpecPat(dc.Pure):
    spec: Spec = dc.field(check_type=Spec)
    pat: Pat = dc.field(check_type=Pat)


def _count_groups(pat: srp.SubPattern) -> int:
    c = 0
    for op, av in pat:
        if op in srm._LITERAL_CODES:  # noqa
            pass
        elif op is srn.IN:
            pass
        elif op is srn.ANY:
            pass
        elif op in srm._REPEATING_CODES:  # noqa
            c += _count_groups(av[2])
        elif op is srn.SUBPATTERN:
            group, add_flags, del_flags, p = av
            if group is not None:
                c += 1
            c += _count_groups(p)
        elif op in srm._SUCCESS_CODES:  # noqa
            raise NotImplementedError
        elif op in srm._ASSERT_CODES:  # noqa
            raise NotImplementedError
        elif op is srn.CALL:
            raise NotImplementedError
        elif op is srn.AT:
            raise NotImplementedError
        elif op is srn.BRANCH:
            raise NotImplementedError
        elif op is srn.CATEGORY:
            pass
        elif op is srn.GROUPREF:
            pass
        elif op is srn.GROUPREF_EXISTS:
            raise NotImplementedError
        else:
            raise TypeError("internal: unsupported operand type %r" % (op,))
    return c


Formatter = ta.Callable[[str], ta.Optional[Pat]]


class SimpleFormatter(dc.Pure):
    spec_s: str = dc.field(check_type=str)
    pat_s: str = dc.field(check_type=str)
    converter: ta.Optional[Converter] = None
    type: ta.Optional[ta.Type] = None

    def __call__(self, s: str) -> ta.Optional[Pat]:
        if s == self.spec_s:
            return Pat(self.pat_s, converter=self.converter, type=self.type)
        else:
            return None


class Match(dc.Pure, ta.Iterable[ta.Any]):
    values: ta.Sequence[ta.Any]
    spans: ta.Sequence[ta.Tuple[int, int]]
    names: ta.Mapping[str, ta.Any]
    idxs: ta.Mapping[str, int]

    def __getitem__(self, key: ta.Union[int, str]) -> ta.Any:
        if isinstance(key, int):
            return self.values[key]
        elif isinstance(key, str):
            return self.names[key]
        else:
            raise TypeError(key)

    def __iter__(self) -> ta.Iterator[ta.Any]:
        return iter(self.values)


def inline_regex_formatter(s: str) -> ta.Optional[Pat]:
    if s.startswith('/'):
        return Pat(s[1:], type=str)
    else:
        return None


class GlyphSplitter:

    def __init__(self, glyphs: ta.Tuple[str, str] = ('{', '}')) -> None:
        super().__init__()

        glyphs = tuple(map(check.of_isinstance(str), glyphs))
        check.state(all(len(s) == 1 for s in glyphs))
        check.state(len(glyphs) == 2)

        self._glyphs = glyphs

        self._double_glyphs: ta.Tuple[str, str] = tuple(s * 2 for s in glyphs)  # noqa
        self._escaped_glyphs: ta.Tuple[str, str] = tuple(map(re.escape, glyphs))  # noqa

        self._lglyph_pat = re.compile(r'(%s)' % (self._escaped_glyphs[0] * 2,))
        self._rglyph_pat = re.compile(r'(%s)' % (self._escaped_glyphs[1] * 2,))
        self._single_glyph_pat = re.compile(r'(%s[^%s]*?%s)' % (
            self._escaped_glyphs[0], self._escaped_glyphs[1], self._escaped_glyphs[1]))

    @dc.dataclass(frozen=True)
    class Match:
        s: str

    def split(self, s: str) -> ta.Sequence[ta.Union['GlyphSplitter.Match', str]]:
        ps = self._lglyph_pat.split(s)
        ps = [p[::-1] for p in ps for p in reversed(self._rglyph_pat.split(p[::-1]))]

        lst = []
        for p in ps:
            if p in self._double_glyphs:
                lst.append(p)
                continue

            ms = list(self._single_glyph_pat.finditer(p))
            if not ms:
                lst.append(p)
                continue

            l = 0
            for i, m in enumerate(ms):
                if m.start() != l:
                    lst.append(p[l:m.start()])
                lst.append(self.Match(p[m.start() + 1:m.end() - 1]))
                l = m.end()

            if l < len(p):
                lst.append(p[l:])

        return lst


class Scanner:

    _DEFAULT_PAT = r'.+?'

    DEFAULT_FORMATTERS: ta.Sequence[Formatter] = [
        SimpleFormatter('', _DEFAULT_PAT, type=str),
        *[SimpleFormatter(c, '\\' + c) for c in 'DsSwW'],
        inline_regex_formatter,
        SimpleFormatter('d', '[0-9]+', lambda s, _: int(s), int),
        SimpleFormatter('n', r'\d{1,3}([,.]\d{3})*', lambda s, _: int(s), int),
        SimpleFormatter('x', r'(0[xX])?[0-9a-fA-F]+', lambda s, _: int(s, 16), int),
        SimpleFormatter('f', r'[0-9]*(\.[0-9]*)?', lambda s, _: float(s), float),
    ]

    def __init__(
            self,
            spec: str,
            *,
            glyphs: ta.Tuple[str, str] = ('{', '}'),
            formatters: ta.Optional[ta.Iterable[Formatter]] = None,
            ws_pat_s: str = ' ',
            ignore_case: bool = False,
    ) -> None:
        super().__init__()

        check.arg(_count_groups(srp.parse(ws_pat_s)) == 0)

        self._spec = check.isinstance(spec, str)
        self._gs = GlyphSplitter(glyphs)
        self._formatters = [check.callable(f) for f in (formatters or self.DEFAULT_FORMATTERS)]
        self._ws_pat_s = ws_pat_s
        self._ignore_case = ignore_case

        pat_s, slots = self._build(spec)
        self._pat_s = pat_s
        self._slots: ta.Sequence[Scanner._Slot] = slots

        flags = 0
        if self._ignore_case:
            flags |= re.I
        self._pat = re.compile(pat_s, flags)

    class _Slot(dc.Pure):
        spec: Spec
        pat: Pat
        num_groups: int

    def _build(self, spec: str) -> ta.Tuple[str, ta.Sequence[_Slot]]:
        lst = [
            p if isinstance(p, str) else self._build_spec(check.isinstance(p, GlyphSplitter.Match).s)
            for p in self._gs.split(spec)
        ]
        check.unique(p.name for p in lst if isinstance(p, Spec) and p.name is not None)

        buf = io.StringIO()
        slots: ta.List[Scanner._Slot] = []
        for p in lst:
            if isinstance(p, str):
                buf.write(re.escape(p))
                continue

            spec = check.isinstance(p, Spec)
            pat = self._build_pat(spec)
            num_groups = _count_groups(srp.parse(pat.s))
            slot = Scanner._Slot(spec, pat, num_groups)
            slots.append(slot)

            s = ''
            if spec.align and spec.align in '<^':
                s += self._ws_pat_s + '*'
            s += '(?'
            if spec.inv_case and not self._ignore_case:
                s += 'i'
            if spec.inv_case and self._ignore_case:
                s += '-i'
            s += ':'
            s += f'({pat.s})'
            s += ')'
            if spec.optional:
                s += '?'
            if spec.align and spec.align in '>^':
                s += self._ws_pat_s + '*'

            buf.write(s)

        return buf.getvalue(), slots

    def _build_spec(self, s: str) -> Spec:
        if not s or s == ':':
            return Spec('')

        if ':' not in s or (s.count(':') == 1 and s[-1] == ':'):
            name, s = s if ':' not in s else s[:-1], ''
        else:
            name, _, s = s.partition(':')

        kw = {}
        if name and not lang.is_ident_start(name[0]):
            if not any(map(lang.is_ident_start, name)):
                ctrl, name = name, None
            else:
                i = next(iter(i for i, c in enumerate(name) if lang.is_ident_start(c)))
                ctrl, name = name[:i], name[i:]

            for c in ctrl:
                if c in '<^>':
                    kw['align'] = c
                elif c == '?':
                    kw['optional'] = True
                elif c == '!':
                    kw['inv_case'] = True
                else:
                    raise ValueError(c)

        if name:
            check.arg(lang.is_ident(name))
        else:
            name = None

        return Spec(s, name, **kw)

    def _build_pat(self, spec: Spec) -> Pat:
        pats = [p for f in self._formatters for p in [f(spec.s)] if p is not None]
        return check.single(pats)

    def scan(self, buf: str) -> ta.Optional[Match]:
        m = self._pat.match(buf)
        if m is None:
            return None
        gs = m.groups()

        values: ta.List[ta.Any] = []
        spans: ta.List[ta.Tuple[int, int]] = []
        names: ta.Dict[str, ta.Any] = {}
        idxs: ta.Dict[str, int] = {}

        i = 0
        for j, slot in enumerate(self._slots):
            s = gs[i]
            i += 1

            sgs = gs[i:i + slot.num_groups]
            i += slot.num_groups

            if slot.pat.converter is not None:
                v = slot.pat.converter(s, sgs)
            else:
                v = s

            values.append(v)
            spans.append(m.span(j + 1))
            if slot.spec.name is not None:
                names[slot.spec.name] = v
                idxs[slot.spec.name] = j

        return Match(values, spans, names, idxs)


def scan(spec: str, s: str, **kwargs) -> ta.Optional[Match]:
    return Scanner(spec, **kwargs).scan(s)
