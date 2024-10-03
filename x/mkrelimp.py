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
        if not lst:
            return in_tks

        first_tk: trt.Token = lst[0]

        if first_tk.name != 'NAME' or first_tk.src not in ('import', 'from'):
            return in_tks
        if not (len(lst) >= 3 and lst[2].name == 'NAME' and lst[2].src == self._mod_name):
            return in_tks

        ##

        e = indexfn(tks.is_ws, lst, 3)
        ip = list(lst[2:e])
        del lst[2:e]
        ps = [t.src for t in ip if t.name == 'NAME']

        ##

        rel_path = os.path.relpath(os.path.join(self._base_dir, *ps[1:]), src_dir)
        sr = rel_path.split(os.sep)
        nr = indexfn(lambda s: s != '..', sr)
        if nr < 0:
            ps = ['.' * (len(sr) + 1)]
        else:
            ps = ['.' * nr, *sr[nr:]]

        ##

        lst[2:2] = interleave(
            trt.Token(name='OP', src='.'),
            [trt.Token(name='NAME', src=p) for p in ps],
        )
        lst[0:0] = pfx
        return lst

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
