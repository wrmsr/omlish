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


def _process_line_tks(
        in_tks: tks.Tokens,
        dir_path: str,
        mod_name: str,
        mod_path: str,
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
    if not (len(lst) >= 3 and lst[2].name == 'NAME' and lst[2].src == mod_name):
        return in_tks

    ##

    e = indexfn(tks.is_ws, lst, 3)
    ip = list(lst[2:e])
    del lst[2:e]
    ps = [t.src for t in ip if t.name == 'NAME']

    ##

    rel_path = os.path.relpath(os.path.join(mod_path, *ps[1:]), dir_path)
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


def _main() -> None:
    mod_path = os.path.join(os.path.dirname(__file__), 'antlr_dev/_runtime')
    check.state(os.path.isdir(mod_path))

    mod_name = 'antlr4'  # os.path.basename(mod_path)
    for dp, dns, fns in os.walk(mod_path):
        for fn in fns:
            if not fn.endswith('.py'):
                continue

            fp = os.path.join(dp, fn)
            with open(fp) as f:
                src = f.read()

            ts = trt.src_to_tokens(src)
            in_ls = tks.split_lines(ts)
            out_ls = [
                _process_line_tks(
                    l,
                    dp,
                    mod_name,
                    mod_path,
                )
                for l in in_ls
            ]
            out_src = tks.join_lines(out_ls)

            with open(fp, 'w') as f:
                f.write(out_src)


if __name__ == '__main__':
    _main()
