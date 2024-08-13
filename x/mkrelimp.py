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
        *,
        start: int = 0,
        stop: int | None = None,
        step: int = 1,
) -> int:
    for i, e in enumerate(itertools.islice(it, start, stop, step)):
        if fn(e):
            return start + i * step
    return -1


def _main() -> None:
    mod_path = 'x/antlr/_vendor/antlr4'
    check.state(os.path.isdir(mod_path))

    mod_name = os.path.basename(mod_path)
    for dp, dns, fns in os.walk(mod_path):
        for fn in fns:
            if not fn.endswith('.py'):
                continue

            print((dp, fn))

            with open(os.path.join(dp, fn)) as f:
                src = f.read()

            ts = trt.src_to_tokens(src)
            ls = tks.split_lines(ts)
            for i, l in enumerate(ls):
                ft: trt.Token = l[0]
                if ft.name != 'NAME' or ft.src not in ('import', 'from'):
                    continue
                if l[4].name == 'NAME' and l[4].src == mod_name:
                    raise NotImplementedError


if __name__ == '__main__':
    _main()
