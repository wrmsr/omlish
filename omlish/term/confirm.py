import sys
import typing as ta


##


def confirm_action(
        message: str | None = None,
        *,
        stdin: ta.Any | None = None,
        stdout: ta.Any | None = None,
) -> bool:
    if stdin is None:
        stdin = sys.stdin
    if not stdin.isatty():
        raise OSError(f'stdin {stdin!r} is not a tty')
    # FIXME: we want to make sure we only run on a tty, but we also want input()'s readline goodies..
    if stdin is not sys.stdin:
        raise RuntimeError('Unsupported stdin')

    if stdout is None:
        stdout = sys.stdout
    if not stdout.isatty():
        raise OSError(f'stdout {stdout!r} is not a tty')

    if message:
        if '\n' in message:
            prefix = message + '\n\n'
        else:
            prefix = message + ' '
    else:
        prefix = ''

    while True:
        c = input(f'{prefix}(y/n): ').lower().strip()

        if c == 'y':
            return True
        elif c == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.", file=stdout)
