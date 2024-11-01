import os
import shutil
import typing as ta


def print_and_join(
        it: ta.Iterable[str],
        *,
        line_len: int | None = None,
        default_to_tty: bool = True,
        default_line_len: int | None = 100,
) -> str:
    if line_len is None:
        if default_to_tty and os.isatty(1):
            default_line_len = shutil.get_terminal_size().columns
        line_len = default_line_len

    def write(c: str) -> None:
        print(c, end='', flush=True)

    x = 0
    lst = []
    for s in it:
        lst.append(s)
        for ln, l in enumerate(s.split('\n')):
            if ln:
                write('\n')
                x = 0

            for wn, w in enumerate(l.split(' ')):
                if line_len is not None and (len(w) + (1 if wn else 0) + x) > line_len:
                    write('\n')
                    x = 0
                elif wn:
                    write(' ')

                write(w)
                x += len(w) + 1

    write('\n')
    return ''.join(lst)
