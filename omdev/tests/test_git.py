"""
['?? a.txt']
['A  a.txt']

[' M a.txt']
['M  a.txt']

[' D a.txt', '?? b.txt']
[' D a.txt', 'A  b.txt']
['R  a.txt -> b.txt']

['?? "difficult \\" filename.txt"']
['A  "difficult \\" filename.txt"']

[' D "difficult \\" filename.txt"', '?? "difficult 2 \\" filename.txt"']
['R  "difficult \\" filename.txt" -> "difficult 2 \\" filename.txt"']
"""
import os.path
import subprocess
import tempfile
import typing as ta

from omlish.diag.debug import debugging_on_exception
from omlish.lite.check import check_state
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


def find_any(s: str, chars: str, start: int = 0) -> int:
    ret = -1
    for c in chars:
        if (found := s.find(c, start)) >= 0 and (ret < 0 or ret > found):
            ret = found
    return ret


def yield_status_line_fields(l: str) -> ta.Iterator[str]:
    p = 0
    while True:
        if l[p] == '"':
            p += 1
            s = []
            while (n := find_any(l, '\\"', p)) > 0:
                if (c := l[n]) == '\\':
                    s.append(l[p:n])
                    s.append(l[n + 1])
                    p = n + 2
                elif c == '"':
                    s.append(l[p:n])
                    p = n
                    break
                else:
                    raise ValueError(l)

            if l[p] != '"':
                raise ValueError(l)

            yield ''.join(s)

            p += 1
            if p == len(l):
                return
            elif l[p] != ' ':
                raise ValueError(l)

            p += 1

        else:
            if (e := l.find(' ', p)) < 0:
                yield l[p:]
                return

            yield l[p:e]
            p = e + 1


def parse_status_line(l: str) -> None:
    for f in yield_status_line_fields(l):
        print(f)


@debugging_on_exception()
def test_parse_status():
    tmp_dir = tempfile.mkdtemp()
    print(f'{tmp_dir=}')

    #

    def run(*cmd: str) -> str:
        return subprocess.check_output(
            subprocess_maybe_shell_wrap_exec(*cmd),
            cwd=tmp_dir,
        ).decode()

    def status() -> list[str]:
        return run('git', 'status', '--porcelain=v1').splitlines()

    def write(file_name: str, contents: str) -> None:
        with open(os.path.join(tmp_dir, file_name), 'w') as f:
            f.write(contents)

    def rename(src: str, dst: str) -> None:
        os.rename(os.path.join(tmp_dir, src), os.path.join(tmp_dir, dst))

    #

    def parse_status():
        # print(status())
        for l in status():
            print(parse_status_line(l))

    #

    run('git', 'init')
    parse_status()

    #

    write('a.txt', '0\n' * 128)
    parse_status()

    run('git', 'add', 'a.txt')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    write('a.txt', '1\n' * 128)
    parse_status()

    run('git', 'add', 'a.txt')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    rename('a.txt', 'b.txt')
    parse_status()

    run('git', 'add', 'b.txt')
    parse_status()

    run('git', 'add', 'a.txt')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    write('difficult " filename.txt', 'foo\n' * 128)
    parse_status()

    run('git', 'add', '.')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    rename('difficult " filename.txt', 'difficult 2 " filename.txt')
    parse_status()

    run('git', 'add', '.')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    write('->.txt', 'abc\n' * 128)
    parse_status()

    run('git', 'add', '.')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()

    #

    rename('->.txt', '-> 2 ->.txt')
    parse_status()

    run('git', 'add', '.')
    parse_status()

    run('git', 'commit', '-m', '--')
    parse_status()
