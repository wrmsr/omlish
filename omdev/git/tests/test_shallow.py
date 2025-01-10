import tempfile

from ..shallow import git_shallow_clone


def test_shallow_subtree():
    td = tempfile.mkdtemp()
    print(td)

    git_shallow_clone(
        base_dir=td,
        repo_url='https://github.com/wrmsr/flaskthing',
        repo_dir='flaskthing',
        rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        repo_subtrees=[],
    )

    #

    td = tempfile.mkdtemp()
    print(td)

    git_shallow_clone(
        base_dir=td,
        repo_url='https://github.com/wrmsr/flaskthing',
        repo_dir='flaskthing',
        rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        repo_subtrees=['README.md'],
    )
