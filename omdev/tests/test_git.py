import os.path
import subprocess
import tempfile

from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ..git import GitStatusItem
from ..git import GitStatusState
from ..git import get_git_status


def test_parse_git_status():
    tmp_dir = tempfile.mkdtemp()
    print(f'{tmp_dir=}')

    #

    def run(*cmd: str) -> str:
        return subprocess.check_output(
            subprocess_maybe_shell_wrap_exec(*cmd),
            cwd=tmp_dir,
        ).decode()

    def status() -> list[GitStatusItem]:
        st = get_git_status(cwd=tmp_dir)
        return list(st)

    def write(file_name: str, contents: str) -> None:
        with open(os.path.join(tmp_dir, file_name), 'w') as f:
            f.write(contents)

    def rename(src: str, dst: str) -> None:
        os.rename(os.path.join(tmp_dir, src), os.path.join(tmp_dir, dst))

    def gsi(xy: str, a: str, b: str | None = None) -> GitStatusItem:
        return GitStatusItem(
            GitStatusState(xy[0]),
            GitStatusState(xy[1]),
            a,
            b,
        )

    #

    run('git', 'init')
    run('git', 'config', 'user.email', 'you@example.com')
    run('git', 'config', 'user.name', 'Your Name')
    assert status() == []

    #

    write('a.txt', '0\n' * 128)
    assert status() == [
        gsi('??', 'a.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsi('A ', 'a.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write('a.txt', '1\n' * 128)
    assert status() == [
        gsi(' M', 'a.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsi('M ', 'a.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename('a.txt', 'b.txt')
    assert status() == [
        gsi(' D', 'a.txt'),
        gsi('??', 'b.txt'),
    ]

    run('git', 'add', 'b.txt')
    assert status() == [
        gsi(' D', 'a.txt'),
        gsi('A ', 'b.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsi('R ', 'a.txt', 'b.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write(difficult_filename := 'difficult " * ? \' \n \t filename.txt', 'foo\n' * 128)
    assert status() == [
        gsi('??', difficult_filename),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsi('A ', difficult_filename),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename(difficult_filename, difficult_filename_2 := 'difficult 2 " filename.txt')
    assert status() == [
        gsi(' D', difficult_filename),
        gsi('??', difficult_filename_2),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsi('R ', difficult_filename, difficult_filename_2),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write('->.txt', 'abc\n' * 128)
    assert status() == [
        gsi('??', '->.txt'),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsi('A ', '->.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename('->.txt', '-> 2 ->.txt')
    assert status() == [
        gsi(' D', '->.txt'),
        gsi('??', '-> 2 ->.txt'),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsi('R ', '->.txt', '-> 2 ->.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []
