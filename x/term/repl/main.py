import sys

from .interact import InteractiveConsole  # noqa
from .interact import run_multiline_interactive_console  # noqa


##


def _main() -> None:
    # set sys.{ps1,ps2} just before invoking the interactive interpreter. This
    # mimics what CPython does in pythonrun.c
    if not hasattr(sys, 'ps1'):
        sys.ps1 = '>>> '
    if not hasattr(sys, 'ps2'):
        sys.ps2 = '... '

    run_multiline_interactive_console(InteractiveConsole())


if __name__ == '__main__':
    _main()
