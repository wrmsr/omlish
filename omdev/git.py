# ruff: noqa: UP006 UP007
# @omlish-lite
"""
git status
  --porcelain=v1
  --ignore-submodules
  2>/dev/null
"""
import dataclasses as dc
import enum
import os.path
import subprocess
import typing as ta

from omlish.lite.check import check_state
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec


##


def git_clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        branch: ta.Optional[str] = None,
        rev: ta.Optional[str] = None,
        repo_subtrees: ta.Sequence[str],
) -> None:
    if not bool(branch) ^ bool(rev):
        raise ValueError('must set branch or rev')

    if isinstance(repo_subtrees, str):
        raise TypeError(repo_subtrees)

    git_opts = [
        '-c', 'advice.detachedHead=false',
    ]

    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'clone',
            '-n',
            '--depth=1',
            '--filter=tree:0',
            *(['-b', branch] if branch else []),
            '--single-branch',
            repo_url,
            repo_dir,
        ),
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'sparse-checkout',
            'set',
            '--no-cone',
            *repo_subtrees,
        ),
        cwd=rd,
    )

    subprocess.check_call(
        subprocess_maybe_shell_wrap_exec(
            'git',
            *git_opts,
            'checkout',
            *([rev] if rev else []),
        ),
        cwd=rd,
    )


def get_git_revision(
        *,
        cwd: ta.Optional[str] = None,
) -> ta.Optional[str]:
    subprocess.check_output(subprocess_maybe_shell_wrap_exec('git', '--version'))

    if cwd is None:
        cwd = os.getcwd()

    if subprocess.run(  # noqa
        subprocess_maybe_shell_wrap_exec(
            'git',
            'rev-parse',
            '--is-inside-work-tree',
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).returncode:
        return None

    has_untracked = bool(subprocess.check_output(subprocess_maybe_shell_wrap_exec(
        'git',
        'ls-files',
        '.',
        '--exclude-standard',
        '--others',
    ), cwd=cwd).decode().strip())

    dirty_rev = subprocess.check_output(subprocess_maybe_shell_wrap_exec(
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ), cwd=cwd).decode().strip()

    return dirty_rev + ('-untracked' if has_untracked else '')


##


_GIT_STATUS_LINE_ESCAPE_CODES: ta.Mapping[str, str] = {
    '\\': '\\',
    '"': '"',
    'n': '\n',
    't': '\t',
}


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
                    s.append(_GIT_STATUS_LINE_ESCAPE_CODES[l[n + 1]])
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


"""
When merge is occurring and was successful, or outside of a merge situation, X shows the status of the index and Y shows
the status of the working tree:
-------------------------------------------------
X         Y       Meaning
-------------------------------------------------
          [AMD]   not updated
M         [ MTD]  updated in index
T         [ MTD]  type changed in index
A         [ MTD]  added to index
D                 deleted from index
R         [ MTD]  renamed in index
C         [ MTD]  copied in index
[MTARC]           index and work tree matches
[ MTARC]  M       work tree changed since index
[ MTARC]  T       type changed in work tree since index
[ MTARC]  D       deleted in work tree
          R       renamed in work tree
          C       copied in work tree

When merge conflict has occurred and has not yet been resolved, X and Y show the state introduced by each head of the
merge, relative to the common ancestor:
-------------------------------------------------
X         Y       Meaning
-------------------------------------------------
D         D       unmerged, both deleted
A         U       unmerged, added by us
U         D       unmerged, deleted by them
U         A       unmerged, added by them
D         U       unmerged, deleted by us
A         A       unmerged, both added
U         U       unmerged, both modified

When path is untracked, X and Y are always the same, since they are unknown to the index:
-------------------------------------------------
X         Y       Meaning
-------------------------------------------------
?         ?       untracked
!         !       ignored

Submodules have more state and instead report

 - M = the submodule has a different HEAD than recorded in the index
 - m = the submodule has modified content
 - ? = the submodule has untracked files

This is since modified content or untracked files in a submodule cannot be added via git add in the superproject to
prepare a commit. m and ? are applied recursively. For example if a nested submodule in a submodule contains an
untracked file, this is reported as ? as well.
"""  # noqa


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


_EXTRA_UNMERGED_GIT_STATUS_LINE_STATES: ta.FrozenSet[ta.Tuple[GitStatusLineState, GitStatusLineState]] = frozenset([
    (GitStatusLineState.ADDED, GitStatusLineState.ADDED),
    (GitStatusLineState.DELETED, GitStatusLineState.DELETED),
])


@dc.dataclass(frozen=True)
class GitStatusLine:
    x: GitStatusLineState
    y: GitStatusLineState

    a: str
    b: ta.Optional[str]

    @property
    def is_unmerged(self) -> bool:
        return (
            self.x is GitStatusLineState.UPDATED_BUT_UNMERGED or
            self.y is GitStatusLineState.UPDATED_BUT_UNMERGED or
            (self.x, self.y) in _EXTRA_UNMERGED_GIT_STATUS_LINE_STATES
        )

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


class GitStatus(ta.Sequence[GitStatusLine]):
    def __init__(self, lines: ta.Iterable[GitStatusLine]) -> None:
        super().__init__()

        self._lst = list(lines)

        by_x: ta.Dict[GitStatusLineState, list[GitStatusLine]] = {}
        by_y: ta.Dict[GitStatusLineState, list[GitStatusLine]] = {}

        by_a: ta.Dict[str, GitStatusLine] = {}
        by_b: ta.Dict[str, GitStatusLine] = {}

        for l in self._lst:
            by_x.setdefault(l.x, []).append(l)
            by_y.setdefault(l.y, []).append(l)

            if l.a in by_a:
                raise KeyError(l.a)
            by_a[l.a] = l

            if l.b is not None:
                if l.b in by_b:
                    raise KeyError(l.b)
                by_b[l.b] = l

        self._by_x = by_x
        self._by_y = by_y

        self._by_a = by_a
        self._by_b = by_b

        self._has_unmerged = any(l.is_unmerged for l in self)

    #

    def __iter__(self) -> ta.Iterator[GitStatusLine]:
        return iter(self._lst)

    def __getitem__(self, index):
        return self._lst[index]

    def __len__(self) -> int:
        return len(self._lst)

    #

    @property
    def by_x(self) -> ta.Mapping[GitStatusLineState, ta.Sequence[GitStatusLine]]:
        return self._by_x

    @property
    def by_y(self) -> ta.Mapping[GitStatusLineState, ta.Sequence[GitStatusLine]]:
        return self._by_y

    @property
    def by_a(self) -> ta.Mapping[str, GitStatusLine]:
        return self._by_a

    @property
    def by_b(self) -> ta.Mapping[str, GitStatusLine]:
        return self._by_b

    #

    @property
    def has_unmerged(self) -> bool:
        return self._has_unmerged

    @property
    def has_staged(self) -> bool:
        return any(l.x != GitStatusLineState.UNMODIFIED for l in self._lst)

    @property
    def has_dirty(self) -> bool:
        return any(l.y != GitStatusLineState.UNMODIFIED for l in self._lst)


def parse_git_status(s: str) -> GitStatus:
    return GitStatus(parse_git_status_line(l) for l in s.splitlines())


def get_git_status(
        *,
        cwd: ta.Optional[str] = None,
        ignore_submodules: bool = False,
        verbose: bool = False,
) -> GitStatus:
    if cwd is None:
        cwd = os.getcwd()

    proc = subprocess.run(  # type: ignore
        subprocess_maybe_shell_wrap_exec(
            'git',
            'status',
            '--porcelain=v1',
            *(['--ignore-submodules'] if ignore_submodules else []),
        ),
        cwd=cwd,
        stdout=subprocess.PIPE,
        **(dict(stderr=subprocess.PIPE) if not verbose else {}),
        check=True,
    )

    return parse_git_status(proc.stdout.decode())  # noqa
