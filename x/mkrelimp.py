import itertools
import os.path
import typing as ta

from omdev import tokens as tks
from omlish import check
import tokenize_rt as trt


T = ta.TypeVar('T')


def indexfn(
        fn: ta.Callable[[T], bool],
        it: ta.Iterable[T],
        start: int = 0,
        stop: int | None = None,
        step: int = 1,
) -> int:
    for i, e in enumerate(itertools.islice(it, start, stop, step)):
        if fn(e):
            return start + i * step
    return -1


def interleave(sep: T, it: ta.Iterable[T]) -> ta.Iterable[T]:
    for i, e in enumerate(it):
        if i > 0:
            yield sep
        yield e


class Processor:
    def __init__(
            self,
            mod_name: str,
            base_dir: str,
    ) -> None:
        super().__init__()
        self._mod_name = mod_name
        self._base_dir = base_dir

    def process_line_tks(
            self,
            in_tks: tks.Tokens,
            src_dir: str,
    ) -> tks.Tokens:
        lst = list(in_tks)
        pfx = []
        while lst and (tks.is_ws(lst[0]) or lst[0].name == 'DEDENT'):
            pfx.append(lst.pop(0))

        if (
                len(lst) < 3 or
                lst[0].name != 'NAME' or
                lst[0].src not in ('import', 'from') or
                lst[2].name != 'NAME' or
                lst[2].src != self._mod_name
        ):
            return in_tks

        ##

        ws_pos = indexfn(tks.is_ws, lst, 3)
        imp_name_tks = list(lst[2:ws_pos])
        imp_name_parts = [t.src for t in imp_name_tks if t.name == 'NAME']

        ##

        rel_path = os.path.relpath(os.path.join(self._base_dir, *imp_name_parts[1:]), src_dir)
        rel_path_parts = rel_path.split(os.sep)
        pd_pos = indexfn(lambda s: s != '..', rel_path_parts)
        if pd_pos < 0:
            rel_imp_name_parts = ['.' * (len(rel_path_parts) + 1)]
        else:
            rel_imp_name_parts = ['.' * pd_pos, *rel_path_parts[pd_pos:]]

        ##

        new_tks = list(interleave(
            trt.Token(name='OP', src='.'),
            [trt.Token(name='NAME', src=p) for p in rel_imp_name_parts],
        ))
        out_tks = [
            *pfx,
            *lst[:2],
            *new_tks,
            *lst[ws_pos:],
        ]
        return out_tks

    def process_file(
            self,
            src_file: str,
    ) -> None:
        with open(src_file) as f:
            src = f.read()

        ts = trt.src_to_tokens(src)
        in_ls = tks.split_lines(ts)
        out_ls = [
            self.process_line_tks(
                l,
                os.path.dirname(src_file),
            )
            for l in in_ls
        ]
        out_src = tks.join_lines(out_ls)

        with open(src_file, 'w') as f:
            f.write(out_src)


def _main() -> None:
    base_dir = os.path.join(os.path.dirname(__file__), 'antlr_dev/_runtime')
    check.state(os.path.isdir(base_dir))
    mod_name = 'antlr4'  # os.path.basename(base_dir)

    p = Processor(
        mod_name,
        base_dir,
    )

    for dp, dns, fns in os.walk(base_dir):
        for fn in fns:
            if not fn.endswith('.py'):
                continue

            p.process_file(os.path.join(dp, fn))


if __name__ == '__main__':
    _main()
