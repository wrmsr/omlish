import tempfile

from ..subtrees import git_clone_subtree


def test_subtree():
    td = tempfile.mkdtemp()
    print(td)

    git_clone_subtree(
        base_dir=td,
        repo_url='https://github.com/wrmsr/flaskthing',
        repo_dir='flaskthing',
        rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        repo_subtrees=[],
    )

    #

    td = tempfile.mkdtemp()
    print(td)

    git_clone_subtree(
        base_dir=td,
        repo_url='https://github.com/wrmsr/flaskthing',
        repo_dir='flaskthing',
        rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        repo_subtrees=['README.md'],
    )
