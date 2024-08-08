import dataclasses as dc
import itertools
import os.path
import pprint
import typing as ta

from omlish import check
import tokenize_rt as trt


##


WS_NAMES = ('UNIMPORTANT_WS', 'NEWLINE', 'COMMENT')


def is_ws(tok: trt.Token) -> bool:
    return tok.name in WS_NAMES


def ignore_ws(toks: ta.Iterable[trt.Token]) -> ta.Iterable[trt.Token]:
    return (t for t in toks if not is_ws(t))


##


@dc.dataclass(frozen=True, kw_only=True)
class Import:
    mod: str
    item: str | None
    as_: str | None

    src_file: str
    line: int

    toks: ta.Sequence[trt.Token] = dc.field(repr=False)


def make_import(
        lts: list[trt.Token],
        src_file: str,
) -> Import | None:
    if not lts:
        return None
    ft = lts[0]

    if ft.name != 'NAME' or ft.src not in ('import', 'from'):
        return None

    ml = []
    il = None
    as_ = None
    for tok in (it := iter(ignore_ws(lts[1:]))):
        if tok.name in ('NAME', 'OP'):
            if tok.src == 'as':
                check.none(as_)
                nt = next(it)
                check.equal(nt.name, 'NAME')
                as_ = nt.src
            elif tok.src == 'import':
                check.equal(ft.src, 'from')
                il = []
            elif il is not None:
                il.append(tok.src)
            else:
                ml.append(tok.src)
        else:
            raise Exception(tok)

    return Import(
        mod=''.join(ml),
        item=''.join(il) if il is not None else None,
        as_=as_,

        src_file=src_file,
        line=ft.line,

        toks=lts,
    )


def _main() -> None:
    root_dir = os.path.dirname(__file__)

    for src_file in [
        'demo/demo.py',
        'demo/stdlib.py',
    ]:
        print(src_file)

        with open(os.path.join(root_dir, src_file)) as f:
            src = f.read()

        print(src)

        toks = trt.src_to_tokens(src)

        tok_lines = [list(it) for g, it in itertools.groupby(toks, lambda t: t.line)]
        pprint.pprint(tok_lines)

        imps = [i for lts in tok_lines if (i := make_import(lts, src_file)) is not None]
        pprint.pprint(imps)

        src2 = trt.tokens_to_src(toks)
        print(src2)


if __name__ == '__main__':
    _main()
