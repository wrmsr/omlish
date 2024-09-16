import os.path
import shutil
import subprocess
import sys
import tempfile
import typing as ta


def clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        repo_subtrees: ta.Sequence[str],
        branch_name: str | None = None,
        rev: str | None = None,
) -> None:
    if not bool(branch_name) ^ bool(rev):
        raise ValueError('must set branch_name or rev')

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
            *(['-b', branch_name] if branch_name else []),
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


def get_local_git_subtree_path(
        *,
        target_dir: str,
        repo_url: str,
        rev: str,
        repo_subtrees: ta.Sequence[str],
) -> str:
    tmp_dir = tempfile.mkdtemp()
    repo_dir = 'repo'

    try:
        clone_subtree(
            base_dir=tmp_dir,
            repo_url=repo_url,
            repo_dir=repo_dir,
            repo_subtrees=repo_subtrees,
            rev=rev,
        )

        full_repo_dir = os.path.join(tmp_dir, repo_dir)
        git_dir = os.path.join(full_repo_dir, '.git')
        if not os.path.isdir(git_dir):
            raise RuntimeError(git_dir)  # noqa
        shutil.rmtree(git_dir)

        return full_repo_dir

    except Exception:
        try:
            shutil.rmtree(tmp_dir)
        except Exception as e2:  # noqa
            print(str(e2), file=sys.stderr)
        raise


if __name__ == '__main__':
    print(get_local_git_subtree_path(
        target_dir=os.path.expanduser('~/.cache/dataplay/wp_movies_10k'),
        repo_url='https://github.com/wrmsr/deep_learning_cookbook',
        repo_subtrees=['data/wp_movies_10k.ndjson'],
        rev='138a99b09ffa3a728d261e461440f029e512ac93',
    ))
