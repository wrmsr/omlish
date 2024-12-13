# ruff: noqa: UP006 UP007
# @omlish-lite
import os.path
import typing as ta

from omlish.subprocesses import subprocesses


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

    subprocesses.check_call(
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
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocesses.check_call(
        'git',
        *git_opts,
        'sparse-checkout',
        'set',
        '--no-cone',
        *repo_subtrees,
        cwd=rd,
    )

    subprocesses.check_call(
        'git',
        *git_opts,
        'checkout',
        *([rev] if rev else []),
        cwd=rd,
    )
