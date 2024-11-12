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

from omlish.diag.debug import debugging_on_exception
from omlish.lite.check import check_state
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


def parse_status_line(l: str) -> None:
    check_state(len(l) > 3, l)
    x, y = l[0], l[1]
    check_state(l[2] == ' ', l)
    p = 3

    def find(cs: str) -> int:
        n = -1
        for c in cs:
            if (f := l.find(c, p)) >= 0 and (n < 0 or n > f):
                n = f
        return n

    if l[p] == '"':
        e = p + 1
        while (n := find('\\"', e)) > 0:
            raise NotImplementedError

    # raise NotImplementedError


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
