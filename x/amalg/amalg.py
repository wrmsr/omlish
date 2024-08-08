import dataclasses as dc
import itertools
import os.path
import pprint  # noqa
import typing as ta

from omlish import check
from omlish import lang
import tokenize_rt as trt


Tokens: ta.TypeAlias = ta.Sequence[trt.Token]


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

    src_path: str
    line: int

    toks: Tokens = dc.field(repr=False)


def make_import(
        lts: Tokens,
        src_path: str,
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

        src_path=src_path,
        line=ft.line,

        toks=lts,
    )


##


@dc.dataclass(frozen=True)
class SrcFile:
    path: str

    @lang.cached_function
    def src(self) -> str:
        with open(self.path) as f:
            return f.read()

    @lang.cached_function
    def tokens(self) -> Tokens:
        return trt.src_to_tokens(self.src())

    @lang.cached_function
    def lines(self) -> ta.Sequence[Tokens]:
        return [list(it) for g, it in itertools.groupby(self.tokens(), lambda t: t.line)]

    @lang.cached_function
    def _process_lines(self) -> tuple[
        ta.Sequence[Import],
        ta.Sequence[Tokens],
    ]:
        imps: list[Import] = []
        ctls: list[Tokens] = []
        for line in self.lines():
            if (imp := make_import(line, self.path)) is not None:
                imps.append(imp)
            else:
                ctls.append(line)
        return imps, ctls

    @lang.cached_function
    def imports(self) -> ta.Sequence[Import]:
        return self._process_lines()[0]

    @lang.cached_function
    def content_lines(self) -> ta.Sequence[Tokens]:
        return self._process_lines()[1]


##


def _main() -> None:
    root_dir = os.path.dirname(__file__)
    main_file = os.path.abspath(os.path.join(root_dir, 'demo/demo.py'))

    src_files: dict[str, SrcFile] = {}
    todo = [main_file]
    while todo:
        src_path = todo.pop()
        if src_path in src_files:
            continue

        f = SrcFile(src_path)
        src_files[src_path] = f
        print(src_path)

        for imp in f.imports():
            print(imp)

            if not imp.mod.startswith('.'):
                continue

            parts = imp.mod.split('.')
            nd = len(parts) - parts[::-1].index('')
            imp_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(src_path),
                    '../' * (nd - 1),
                    *parts[nd:-1],
                    parts[-1] + '.py',
                ),
            )
            todo.append(check.isinstance(imp_path, str))

        print()


if __name__ == '__main__':
    _main()
