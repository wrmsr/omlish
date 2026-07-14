from ..cache import is_repo_cached


def test_is_repo_cached():
    assert isinstance(is_repo_cached('Qwen/Qwen3-Coder-30B-A3B-Instruct'), bool)
