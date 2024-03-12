import os.path
import subprocess


def clone_branch_subtree(
        *,
        base_dir: str,
        repo_url: str,
        repo_dir: str,
        repo_subtree: str,
        branch_name: str,
) -> None:
    subprocess.check_call(
        [
            'git',
            'clone',
            '-n',
            '--depth=1',
            '--filter=tree:0',
            '-b', branch_name,
            '--single-branch',
            '-o', repo_dir,
            repo_url,
        ],
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        [
            'git',
            'sparse-checkout',
            'set',
            '--no-cone',
            repo_subtree,
        ],
        cwd=rd,
    )
    subprocess.check_call(['git', 'checkout'], cwd=rd)


# def clone_rev_subtree(
#         *,
#         base_dir: str,
#         repo_url: str,
#         repo_dir: str,
#         repo_subtree: str,
#         rev: str | None = None,
# ) -> None:
#     if not bool(branch_name) ^ bool(rev):
#         raise ValueError('must set branch_name or rev')
#
#     subprocess.check_call(
#         [
#             'git',
#             'clone',
#             '-n',
#             '--depth=1',
#             '--filter=tree:0',
#             '--single-branch',
#             '-o', repo_dir,
#             repo_url,
#         ],
#         cwd=base_dir,
#     )
#
#     rd = os.path.join(base_dir, repo_dir)
#     subprocess.check_call(
#         [
#             'git',
#             'sparse-checkout',
#             'set',
#             '--no-cone',
#             repo_subtree,
#         ],
#         cwd=rd,
#     )
#     subprocess.check_call(['git', 'checkout'], cwd=rd)


if __name__ == '__main__':
    clone_branch_subtree(
        base_dir=os.getcwd(),
        repo_url='https://github.com/wrmsr/deep_learning_cookbook',
        branch_name='master',
        # rev='138a99b09ffa3a728d261e461440f029e512ac93',
        repo_dir='deep_learning_cookbook',
        repo_subtree='data/wp_movies_10k.ndjson',
    )
