# ruff: noqa: UP006 UP045
# @omlish-lite
"""
https://www.brandur.org/logfmt
"""
import re
import typing as ta


##


_LOGFMT_ENCODE_WS_PAT = re.compile(r'[\s"]')


def logfmt_encode(
        dct: ta.Mapping[str, ta.Optional[ta.Any]],
        *,
        value_encoder: ta.Optional[ta.Callable[[ta.Any], ta.Optional[str]]] = None,
) -> str:
    def encode(s: str) -> str:
        if _LOGFMT_ENCODE_WS_PAT.search(s) is not None:
            s = s.replace('\\', '\\\\')
            s = s.replace('\n', '\\n')
            s = s.replace('"', '\\"')
            return f'"{s}"'
        else:
            return s

    if value_encoder is None:
        value_encoder = str

    lst: ta.List[str] = []
    for k, v in dct.items():
        ps: ta.List[str]
        if v is None:
            continue
        elif v is True:
            ps = [k]
        elif isinstance(v, str):
            ps = [k, v]
        elif (v := value_encoder(v)) is None:
            continue
        else:
            ps = [k, v]

        lst.append('='.join(map(encode, ps)))

    return ' '.join(lst)


#


_LOGFMT_DECODE_PAT_PART = r'[^"=\s]+|("([^\\]|(\\.))*?")'
_LOGFMT_DECODE_PAT = re.compile(
    rf'\s*'
    rf'(?P<key>{_LOGFMT_DECODE_PAT_PART})'
    rf'(=(?P<value>{_LOGFMT_DECODE_PAT_PART}))?'
    rf'\s*',
)


def logfmt_decode(
        line: str,
        *,
        value_decoder: ta.Optional[ta.Callable[[str], ta.Optional[ta.Any]]] = None,
) -> ta.Dict[str, ta.Any]:
    def unquote(s: str) -> str:
        if s.startswith('"'):
            if len(s) < 2 or not s.endswith('"'):
                raise ValueError(s)
            s = s[1:-1]
            s = s.replace('\\"', '"')
            s = s.replace('\\n', '\n')
            s = s.replace('\\\\', '\\')
        return s

    if value_decoder is None:
        def value_decoder(s: str) -> ta.Any:
            try:
                return int(s)
            except ValueError:
                pass
            try:
                return float(s)
            except ValueError:
                pass
            return s

    dct: ta.Dict[str, ta.Any] = {}
    p = 0
    while True:
        m = _LOGFMT_DECODE_PAT.match(line, p)
        if m is None:
            break
        if m.start() != p:
            raise RuntimeError

        k = unquote(m.group('key'))
        if k in dct:
            raise KeyError(k)

        vs = m.group('value')
        v: ta.Any
        if vs is None:
            v = True
        else:
            v = value_decoder(unquote(vs))

        dct[k] = v
        p = m.end()

    if p < len(line):
        raise ValueError(f'Unconsumed logfmt input: {line[p:]}')

    return dct
