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


def _main() -> None:
    mod_path = 'x/antlr/_vendor/antlr4'
    check.state(os.path.isdir(mod_path))

    mod_name = os.path.basename(mod_path)
    for dp, dns, fns in os.walk(mod_path):
        for fn in fns:
            if not fn.endswith('.py'):
                continue

            with open(os.path.join(dp, fn)) as f:
                src = f.read()

            ts = trt.src_to_tokens(src)
            ls = tks.split_lines(ts)
            for l in ls:
                ft: trt.Token = l[0]
                if ft.name != 'NAME' or ft.src not in ('import', 'from'):
                    continue
                if len(l) >= 3 and l[2].name == 'NAME' and l[2].src == mod_name:
                    print(tks.join_toks(l).strip())

                    ##

                    e = indexfn(tks.is_ws, l, 3)
                    ip = list(l[2:e])
                    del l[2:e]
                    ps = [t.src for t in ip if t.name == 'NAME']

                    ##

                    print((dp, fn))
                    print(ps)
                    rel_path = os.path.relpath(os.path.join(mod_path, *ps[1:]), dp)
                    print(rel_path)

                    ##

                    l[2:2] = interleave(
                        trt.Token(name='OP', src='.'),
                        [trt.Token(name='NAME', src=p) for p in ps],
                    )

                    ##

                    print(tks.join_toks(l).strip())
                    print()


if __name__ == '__main__':
    _main()
