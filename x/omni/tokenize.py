import io
import tokenize
import typing as ta

from . import iterables as it


def yield_toks(s: str) -> ta.Iterator[tokenize.TokenInfo]:
    return iter(tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline))


def brace_indent_toks(
        toks: ta.Iterable[tokenize.TokenInfo],
        out: ta.TextIO,
        *,
        indent: str = '    ',
) -> None:
    # Same scheme as https://github.com/umlet/pwk/
    indents = 0
    braces = 0

    for lt, t in it.pairwise(toks, None):
        if t.type == tokenize.ENCODING:
            continue

        if t.type == tokenize.OP:
            if t.string == ';':
                out.write('\n')
                out.write(indent * indents)
                continue

            if t.string == ':' and not braces:
                indents += 1
                out.write(':\n')
                out.write(indent * indents)
                continue

            if t.string == '{':
                if lt and lt.type == tokenize.OP and lt.string == ':':
                    continue
                braces += 1

            if t.string == '}':
                if braces:
                    braces -= 1
                elif indents:
                    indents -= 1
                    out.write('\n')
                    out.write(indent * indents)
                    continue
                else:
                    raise Exception('Negative dedent')

        out.write(t.string)
        out.write(' ')

    out.write('\n')


def brace_indent(s: str, **kwargs) -> str:
    out = io.StringIO()
    brace_indent_toks(yield_toks(s), out, **kwargs)
    return out.getvalue()
