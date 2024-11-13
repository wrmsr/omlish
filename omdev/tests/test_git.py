import os.path
import subprocess
import tempfile

from omlish.diag.debug import debugging_on_exception
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ..git import GitStatusLine
from ..git import GitStatusLineState
from ..git import get_git_status


@debugging_on_exception()
def test_parse_git_status():
    tmp_dir = tempfile.mkdtemp()
    print(f'{tmp_dir=}')

    #

    def run(*cmd: str) -> str:
        return subprocess.check_output(
            subprocess_maybe_shell_wrap_exec(*cmd),
            cwd=tmp_dir,
        ).decode()

    def status() -> list[GitStatusLine]:
        st = get_git_status(cwd=tmp_dir)
        return list(st)

    def write(file_name: str, contents: str) -> None:
        with open(os.path.join(tmp_dir, file_name), 'w') as f:
            f.write(contents)

    def rename(src: str, dst: str) -> None:
        os.rename(os.path.join(tmp_dir, src), os.path.join(tmp_dir, dst))

    def gsl(xy: str, a: str, b: str | None = None) -> GitStatusLine:
        return GitStatusLine(
            GitStatusLineState(xy[0]),
            GitStatusLineState(xy[1]),
            a,
            b,
        )

    #

    run('git', 'init')
    assert status() == []

    #

    write('a.txt', '0\n' * 128)
    assert status() == [
        gsl('??', 'a.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsl('A ', 'a.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write('a.txt', '1\n' * 128)
    assert status() == [
        gsl(' M', 'a.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsl('M ', 'a.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename('a.txt', 'b.txt')
    assert status() == [
        gsl(' D', 'a.txt'),
        gsl('??', 'b.txt'),
    ]

    run('git', 'add', 'b.txt')
    assert status() == [
        gsl(' D', 'a.txt'),
        gsl('A ', 'b.txt'),
    ]

    run('git', 'add', 'a.txt')
    assert status() == [
        gsl('R ', 'a.txt', 'b.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write(difficult_filename := 'difficult " filename.txt', 'foo\n' * 128)
    assert status() == [
        gsl('??', difficult_filename),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsl('A ', difficult_filename),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename(difficult_filename, difficult_filename_2 := 'difficult 2 " filename.txt')
    assert status() == [
        gsl(' D', difficult_filename),
        gsl('??', difficult_filename_2),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsl('R ', difficult_filename, difficult_filename_2),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    write('->.txt', 'abc\n' * 128)
    assert status() == [
        gsl('??', '->.txt'),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsl('A ', '->.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []

    #

    rename('->.txt', '-> 2 ->.txt')
    assert status() == [
        gsl(' D', '->.txt'),
        gsl('??', '-> 2 ->.txt'),
    ]

    run('git', 'add', '.')
    assert status() == [
        gsl('R ', '->.txt', '-> 2 ->.txt'),
    ]

    run('git', 'commit', '-m', '--')
    assert status() == []
