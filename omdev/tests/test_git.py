import os.path
import subprocess
import tempfile

from omlish.diag.debug import debugging_on_exception
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ..git import parse_git_status


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

    def status() -> str:
        return run('git', 'status', '--porcelain=v1')

    def write(file_name: str, contents: str) -> None:
        with open(os.path.join(tmp_dir, file_name), 'w') as f:
            f.write(contents)

    def rename(src: str, dst: str) -> None:
        os.rename(os.path.join(tmp_dir, src), os.path.join(tmp_dir, dst))

    #

    run('git', 'init')
    print(parse_git_status(status()))

    #

    write('a.txt', '0\n' * 128)
    print(parse_git_status(status()))

    run('git', 'add', 'a.txt')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    write('a.txt', '1\n' * 128)
    print(parse_git_status(status()))

    run('git', 'add', 'a.txt')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    rename('a.txt', 'b.txt')
    print(parse_git_status(status()))

    run('git', 'add', 'b.txt')
    print(parse_git_status(status()))

    run('git', 'add', 'a.txt')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    write('difficult " filename.txt', 'foo\n' * 128)
    print(parse_git_status(status()))

    run('git', 'add', '.')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    rename('difficult " filename.txt', 'difficult 2 " filename.txt')
    print(parse_git_status(status()))

    run('git', 'add', '.')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    write('->.txt', 'abc\n' * 128)
    print(parse_git_status(status()))

    run('git', 'add', '.')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))

    #

    rename('->.txt', '-> 2 ->.txt')
    print(parse_git_status(status()))

    run('git', 'add', '.')
    print(parse_git_status(status()))

    run('git', 'commit', '-m', '--')
    print(parse_git_status(status()))
