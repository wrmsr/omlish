import argparse
import itertools
import os.path
import typing as ta

from omlish.logs import all as logs

from ...cli import CliModule
from ..tokens import all as tks


T = ta.TypeVar('T')


log = logs.get_module_logger(globals())


##


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


def interleave(sep: T, it: ta.Iterable[T]) -> ta.Iterator[T]:
    for i, e in enumerate(it):
        if i > 0:
            yield sep
        yield e


class Processor:
    def __init__(
            self,
            base_dir: str,
            mod_name: str | None = None,
            *,
            write: bool = False,
    ) -> None:
        super().__init__()

        self._base_dir = base_dir
        self._mod_name = mod_name if mod_name is not None else os.path.basename(base_dir)
        self._write = write

    def process_line_tks(
            self,
            in_tks: tks.Tokens,
            src_file: str,
    ) -> tks.Tokens:
        lst = list(in_tks)
        pfx = []
        while lst and (tks.is_ws(lst[0]) or lst[0].name in ('INDENT', 'DEDENT')):
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

        src_dir = os.path.dirname(src_file)
        rel_path = os.path.relpath(os.path.join(self._base_dir, *imp_name_parts[1:]), src_dir)
        rel_path_parts = rel_path.split(os.sep)
        pd_pos = indexfn(lambda s: s != '..', rel_path_parts)
        if pd_pos < 0:
            rel_imp_name_parts = ['.' * (len(rel_path_parts) + 1)]
        else:
            rel_imp_name_parts = ['.' * pd_pos, *rel_path_parts[pd_pos:]]

        ##

        new_tks = list(interleave(
            tks.Token(name='OP', src='.'),
            [tks.Token(name='NAME', src=p) for p in rel_imp_name_parts],
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
        log.info('Processing file: %s : %s', self._mod_name, src_file)

        with open(src_file) as f:
            src = f.read()

        ts = tks.src_to_tokens(src)
        in_ls = tks.split_lines(ts)
        out_ls = [
            self.process_line_tks(
                l,
                src_file,
            )
            for l in in_ls
        ]
        out_src = tks.join_lines(out_ls)

        if self._write:
            with open(src_file, 'w') as f:
                f.write(out_src)

        else:
            print(out_src)
            print()

    def process_dir(
            self,
            base_dir: str,
    ) -> None:
        for dp, _, fns in os.walk(base_dir):
            for fn in fns:
                if not fn.endswith('.py'):
                    continue

                self.process_file(os.path.join(dp, fn))

    def process(self) -> None:
        self.process_dir(self._base_dir)


# @omlish-manifest
_CLI_MODULE = CliModule('py/mkrelimp', __name__)


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('base_dir')
    parser.add_argument('mod_name', nargs='?')
    parser.add_argument('-w', '--write', action='store_true')
    args = parser.parse_args()

    logs.configure_standard_logging('INFO')

    Processor(
        args.base_dir,
        args.mod_name,
        write=args.write,
    ).process()


if __name__ == '__main__':
    _main()
