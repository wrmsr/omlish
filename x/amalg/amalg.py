"""
TODO:
 - shebang
 - hoist initial docstring/comments

Targets:
 - interp
 - pyproject
 - precheck
 - build
 - pyremote
 - bootstrap
 - deploy
 - supervisor?
"""
import dataclasses as dc
import io
import itertools
import os.path
import pprint  # noqa
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang
import tokenize_rt as trt


Tokens: ta.TypeAlias = ta.Sequence[trt.Token]


##


WS_NAMES = ('UNIMPORTANT_WS', 'NEWLINE', 'COMMENT')


def is_ws(tok: trt.Token) -> bool:
    return tok.name in WS_NAMES


def ignore_ws(toks: ta.Iterable[trt.Token]) -> ta.Iterable[trt.Token]:
    return (t for t in toks if not is_ws(t))


def join_toks(ts: Tokens) -> str:
    return ''.join(t.src for t in ts)


##


@dc.dataclass(frozen=True, kw_only=True)
class Import:
    mod: str
    item: str | None
    as_: str | None

    src_path: str
    line: int

    toks: Tokens = dc.field(repr=False)

    @lang.cached_property
    def mod_path(self) -> str | None:
        if not self.mod.startswith('.'):
            return None

        parts = self.mod.split('.')
        nd = len(parts) - parts[::-1].index('')
        mod_path = os.path.abspath(
            os.path.join(
                os.path.dirname(self.src_path),
                '../' * (nd - 1),
                *parts[nd:-1],
                parts[-1] + '.py',
            ),
        )

        return check.isinstance(mod_path, str)


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


@dc.dataclass(frozen=True, kw_only=True)
class Typing:
    src: str

    src_path: str
    line: int

    toks: Tokens = dc.field(repr=False)


def make_typing(
        lts: Tokens,
        src_path: str,
) -> Typing | None:
    if not lts or lts[0].name == 'UNIMPORTANT_WS':
        return None

    wts = list(ignore_ws(lts))
    if not (
            len(wts) >= 5 and
            wts[0].name == 'NAME' and
            wts[1].name == 'OP' and wts[1].src == '=' and
            wts[2].name == 'NAME' and wts[2].src == 'ta' and
            wts[3].name == 'OP' and wts[3].src == '.'

    ):
        return None

    return Typing(
        src=join_toks(lts),

        src_path=src_path,
        line=wts[0].line,

        toks=lts,
    )


##


@dc.dataclass(frozen=True)
class SrcFile:
    path: str

    @lang.cached_function
    def src(self) -> str:
        with open(self.path) as f:
            return f.read().strip()

    @lang.cached_function
    def tokens(self) -> Tokens:
        return trt.src_to_tokens(self.src())

    @lang.cached_function
    def lines(self) -> ta.Sequence[Tokens]:
        return [list(it) for g, it in itertools.groupby(self.tokens(), lambda t: t.line)]

    @lang.cached_function
    def _process_lines(self) -> tuple[
        ta.Sequence[Import],
        ta.Sequence[Typing],
        ta.Sequence[Tokens],
    ]:
        imps: list[Import] = []
        tys: list[Typing] = []
        ctls: list[Tokens] = []
        for line in self.lines():
            if (imp := make_import(line, self.path)) is not None:
                imps.append(imp)
            elif (ty := make_typing(line, self.path)) is not None:
                tys.append(ty)
            else:
                ctls.append(line)
        return imps, tys, ctls

    @lang.cached_function
    def imports(self) -> ta.Sequence[Import]:
        return self._process_lines()[0]

    @lang.cached_function
    def typings(self) -> ta.Sequence[Typing]:
        return self._process_lines()[1]

    @lang.cached_function
    def content_lines(self) -> ta.Sequence[Tokens]:
        return self._process_lines()[2]


##


SECTION_SEP = '#' * 40 + '\n'


def _main() -> None:
    root_dir = os.path.dirname(__file__)
    for main_file in [
        'demo/demo.py',
        'demo/deploy/deploy.py',
        'demo/interp/interp.py',
        'demo/pyproject/pyproject.py',
    ]:
        main_path = os.path.abspath(os.path.join(root_dir, main_file))

        src_files: dict[str, SrcFile] = {}
        todo = [main_path]
        while todo:
            src_path = todo.pop()
            if src_path in src_files:
                continue

            f = SrcFile(src_path)
            src_files[src_path] = f

            for imp in f.imports():
                if (mp := imp.mod_path) is not None:
                    todo.append(mp)

        ##

        out = io.StringIO()

        ##

        all_imps = [i for f in src_files.values() for i in f.imports()]
        gl_imps = [i for i in all_imps if i.mod_path is None]

        dct = {}
        for imp in gl_imps:
            dct.setdefault((k := (imp.mod, imp.item, imp.as_)), []).append(imp)
        for _, l in sorted(dct.items()):
            out.write(join_toks(l[0].toks))
        if dct:
            out.write('\n\n')

        ##

        ts = list(col.toposort({
            f.path: {mp for i in f.imports() if (mp := i.mod_path) is not None}
            for f in src_files.values()
        }))
        sfs = [sf for ss in ts for sf in sorted(ss)]

        ##

        tys = set()
        for sf in sfs:
            f = src_files[sf]
            for ty in f.typings():
                if ty.src not in tys:
                    out.write(ty.src)
                    tys.add(ty.src)
        if tys:
            out.write('\n\n')

        ##

        for i, sf in enumerate(sfs):
            f = src_files[sf]
            out.write(SECTION_SEP)
            out.write(f'# {f.path}\n\n\n')
            sf_src = ''.join(join_toks(cl) for cl in f.content_lines())
            out.write(sf_src.strip())
            if i < len(sfs) - 1:
                out.write('\n\n\n')
            else:
                out.write('\n')

        ##

        print(out.getvalue())

        with open(os.path.join(root_dir, 'out', os.path.basename(main_file).rpartition('.')[0] + '_amalg.py'), 'w') as f:
            f.write(out.getvalue())


if __name__ == '__main__':
    _main()
