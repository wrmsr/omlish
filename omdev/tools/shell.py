import shlex
import typing as ta

from omlish import check
from omlish.argparse import all as ap
from omlish.formats import json

from ..cli.types import CliModule


##


DEFAULT_DELIMITER = ' '


def _print_list(
        lst: ta.Iterable[str],
        *,
        delimiter: str | None = None,
) -> None:
    check.not_isinstance(lst, str)

    if delimiter is None:
        delimiter = DEFAULT_DELIMITER

    for e in lst:
        check.not_in(delimiter, e)

    print(delimiter.join(lst))


##


class ShellCli(ap.Cli):
    @ap.cmd(
        ap.arg('strs', nargs='*'),
        ap.arg('--delimiter', '-d'),
    )
    def quote(self) -> None:
        _print_list(
            [shlex.quote(e) for e in self.args.strs],
            delimiter=self.args.delimiter,
        )

    #

    _PREFIX_OR_INTERLEAVE_ARGS: ta.ClassVar[ta.Sequence[ta.Any]] = [
        ap.arg('--quote', '-q', action='store_true'),
        ap.arg('--delimiter', '-d'),
    ]

    def _prefix_or_interleave(
            self,
            mode: ta.Literal['prefix', 'interleave'],
            separator: str,
            items: ta.Iterable[str],
    ) -> None:
        lst = []

        for i, e in enumerate(check.not_isinstance(items, str)):
            if i or mode != 'interleave':
                lst.append(separator)

            if self.args.quote:
                e = shlex.quote(e)

            lst.append(e)

        _print_list(
            lst,
            delimiter=self.args.delimiter,
        )

    @ap.cmd(
        ap.arg('prefix'),
        ap.arg('items', nargs='*'),
        *_PREFIX_OR_INTERLEAVE_ARGS,
    )
    def prefix(self) -> None:
        self._prefix_or_interleave(
            'prefix',
            self.args.prefix,
            self.args.items,
        )

    @ap.cmd(
        ap.arg('separator'),
        ap.arg('items', nargs='*'),
        *_PREFIX_OR_INTERLEAVE_ARGS,
    )
    def interleave(self) -> None:
        self._prefix_or_interleave(
            'interleave',
            self.args.separator,
            self.args.items,
        )

    #

    @ap.cmd(accepts_unknown=True)
    def argv(self) -> None:
        print(json.dumps_pretty(self.unknown_args))


##


# @omlish-manifest
_CLI_MODULE = CliModule(['shell', 'sh'], __name__)


def _main() -> None:
    ShellCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
