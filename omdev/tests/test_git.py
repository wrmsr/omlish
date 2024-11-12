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
import dataclasses as dc
import enum
import os.path
import subprocess
import tempfile
import typing as ta

from omlish.diag.debug import debugging_on_exception
from omlish.lite.check import check_state
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


def yield_git_status_line_fields(l: str) -> ta.Iterator[str]:
    def find_any(chars: str, start: int = 0) -> int:
        ret = -1
        for c in chars:
            if (found := l.find(c, start)) >= 0 and (ret < 0 or ret > found):
                ret = found
        return ret

    p = 0
    while True:
        if l[p] == '"':
            p += 1
            s = []
            while (n := find_any('\\"', p)) > 0:
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


class GitStatusLineState(enum.Enum):
    UNMODIFIED = ' '
    MODIFIED = 'M'
    FILE_TYPE_CHANGED = 'T'
    ADDED = 'A'
    DELETED = 'D'
    RENAMED = 'R'
    COPIED = 'C'
    UPDATED_BUT_UNMERGED = 'U'
    UNTRACKED = '?'
    IGNORED = '!'
    SUBMODULE_MODIFIED_CONTENT = 'm'


"""
# X          Y     Meaning
# -------------------------------------------------
#          [AMD]   not updated
# M        [ MTD]  updated in index
# T        [ MTD]  type changed in index
# A        [ MTD]  added to index
# D                deleted from index
# R        [ MTD]  renamed in index
# C        [ MTD]  copied in index
# [MTARC]          index and work tree matches
# [ MTARC]    M    work tree changed since index
# [ MTARC]    T    type changed in work tree since index
# [ MTARC]    D    deleted in work tree
#             R    renamed in work tree
#             C    copied in work tree
# -------------------------------------------------
# D           D    unmerged, both deleted
# A           U    unmerged, added by us
# U           D    unmerged, deleted by them
# U           A    unmerged, added by them
# D           U    unmerged, deleted by us
# A           A    unmerged, both added
# U           U    unmerged, both modified
# -------------------------------------------------
# ?           ?    untracked
# !           !    ignored
# -------------------------------------------------
# 
# Submodules have more state and instead report
# 
#  - M = the submodule has a different HEAD than recorded in the index
#  - m = the submodule has modified content
#  - ? = the submodule has untracked files
"""  # noqa


@dc.dataclass(frozen=True)
class GitStatusLine:
    x: GitStatusLineState
    y: GitStatusLineState

    a: str
    b: str | None

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'x={self.x.name}, '
            f'y={self.y.name}, '
            f'a={self.a!r}' +
            (f', b={self.b!r}' if self.b is not None else '') +
            ')'
        )


def parse_git_status_line(l: str) -> GitStatusLine:
    if len(l) < 3 or l[2] != ' ':
        raise ValueError(l)
    x, y = l[0], l[1]

    fields = list(yield_git_status_line_fields(l[3:]))
    if len(fields) == 1:
        a, b = fields[0], None
    elif len(fields) == 3:
        check_state(fields[1] == '->', l)
        a, b = fields[0], fields[2]
    else:
        raise ValueError(l)

    return GitStatusLine(
        GitStatusLineState(x),
        GitStatusLineState(y),
        a,
        b,
    )


def parse_git_status(s: str) -> list[GitStatusLine]:
    return [parse_git_status_line(l) for l in s.splitlines()]


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
