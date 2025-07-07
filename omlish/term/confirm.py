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

    if stdout is None:
        stdout = sys.stdout
    if not stdout.isatty():
        raise OSError(f'stdout {stdout!r} is not a tty')

    while True:
        if message and not message[-1].isspace():
            if '\n' in message:
                prefix = message + '\n\n'
            else:
                prefix = message + ' '
        else:
            prefix = ''

        c = input(f'{prefix}(y/n): ').lower().strip()

        if c == 'y':
            return True
        elif c == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")
