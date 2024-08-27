import os.path
import shutil
import subprocess
import sys
import tempfile


def clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        repo_subtree: str,
        branch_name: str | None = None,
        rev: str | None = None,
) -> None:
    if not bool(branch_name) ^ bool(rev):
        raise ValueError('must set branch_name or rev')

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
            repo_subtree,
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
        repo_subtree: str,
) -> str:
    tmp_path = tempfile.mkdtemp()
    try:
        clone_subtree(
            base_dir=tmp_path,
            repo_url=repo_url,
            repo_dir='repo',
            repo_subtree=repo_subtree,
            rev=rev,
        )
        local_path = os.path.join(tmp_path, 'repo', repo_subtree)
        if not os.path.exists(local_path):
            raise RuntimeError(local_path)
        os.rename(local_path, target_dir)
    except Exception:
        try:
            shutil.rmtree(tmp_path)
        except Exception as e2:
            print(str(e2), file=sys.stderr)
        raise
    else:
        return target_dir


if __name__ == '__main__':
    print(get_local_git_subtree_path(
        target_dir=os.path.expanduser('~/.cache/dataplay/wp_movies_10k'),
        repo_url='https://github.com/wrmsr/deep_learning_cookbook',
        repo_subtree='data/wp_movies_10k.ndjson',
        rev='138a99b09ffa3a728d261e461440f029e512ac93',
    ))
