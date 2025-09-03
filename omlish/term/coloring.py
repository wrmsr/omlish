# @omlish-lite
import abc
import enum
import os
import typing as ta

from ..lite.abstract import Abstract


##


class TermColor(enum.Enum):
    RED = enum.auto()
    GREEN = enum.auto()
    YELLOW = enum.auto()
    BLUE = enum.auto()


class TermColoring(Abstract):
    @abc.abstractmethod
    def color(self, c: TermColor, s: str) -> str:
        raise NotImplementedError

    def red(self, s: str, **kwargs: ta.Any) -> str:
        return self.color(TermColor.RED, s, **kwargs)

    def green(self, s: str, **kwargs: ta.Any) -> str:
        return self.color(TermColor.GREEN, s, **kwargs)

    def yellow(self, s: str, **kwargs: ta.Any) -> str:
        return self.color(TermColor.YELLOW, s, **kwargs)

    def blue(self, s: str, **kwargs: ta.Any) -> str:
        return self.color(TermColor.BLUE, s, **kwargs)


class NopTermColoring(TermColoring):
    def color(self, c: TermColor, s: str) -> str:
        return s


class AnsiTermColoring(TermColoring):
    _COLOR_CODES: ta.ClassVar[ta.Mapping[TermColor, str]] = {
        TermColor.RED: '\033[31m',
        TermColor.GREEN: '\033[32m',
        TermColor.YELLOW: '\033[33m',
        TermColor.BLUE: '\033[34m',
    }

    _RESET_CODE = '\033[0m'

    def color(self, c: TermColor, s: str) -> str:
        return f'{self._COLOR_CODES[c]}{s}{self._RESET_CODE}'


def term_coloring(
        *,
        forced: bool = False,
        disabled: bool = False,
        file: ta.Any = None,
) -> TermColoring:
    if not forced:
        if not disabled:
            if file is not None:
                if hasattr(file, 'isatty'):
                    if not file.isatty():
                        disabled = True
                elif isinstance(file, int):
                    if not os.isatty(file):
                        disabled = True
                else:
                    raise TypeError(file)

        if disabled:
            return NopTermColoring()

    return AnsiTermColoring()


##


if __name__ == '__main__':
    def _main() -> None:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--disable', action='store_true')
        args = parser.parse_args()

        import sys

        tc = term_coloring(
            forced=args.force,
            disabled=args.disable,
            file=sys.stdout,
        )

        print('\n'.join([
            'normal',
            tc.red('red'),
            tc.green('green'),
            tc.yellow('yellow'),
            tc.blue('blue'),
            'normal',
        ]))

    _main()
