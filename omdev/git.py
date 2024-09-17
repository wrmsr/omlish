# ruff: noqa: UP007
# @omlish-lite
import os.path
import subprocess
import typing as ta


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
        [
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
        ],
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        [
            'git',
            *git_opts,
            'sparse-checkout',
            'set',
            '--no-cone',
            *repo_subtrees,
        ],
        cwd=rd,
    )

    subprocess.check_call(
        [
            'git',
            *git_opts,
            'checkout',
            *([rev] if rev else []),
        ],
        cwd=rd,
    )


def get_git_revision(
        *,
        cwd: ta.Optional[str] = None,
) -> ta.Optional[str]:
    subprocess.check_output(['git', '--version'])

    if cwd is None:
        cwd = os.getcwd()

    if subprocess.run([  # noqa
        'git',
        'rev-parse',
        '--is-inside-work-tree',
    ], stderr=subprocess.PIPE).returncode:
        return None

    has_untracked = bool(subprocess.check_output([
        'git',
        'ls-files',
        '.',
        '--exclude-standard',
        '--others',
    ], cwd=cwd).decode().strip())

    dirty_rev = subprocess.check_output([
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ], cwd=cwd).decode().strip()

    return dirty_rev + ('-untracked' if has_untracked else '')
