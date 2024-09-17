import pytest

from .. import defaults
from .. import specs


@pytest.mark.online
def test_default():
    from omlish import logs

    logs.configure_standard_logging('INFO')

    #

    for spec in [
        specs.GitCacheDataSpec(
            'https://github.com/wrmsr/deep_learning_cookbook',
            rev='138a99b09ffa3a728d261e461440f029e512ac93',
            subtrees=['data/wp_movies_10k.ndjson'],
        ),
        specs.GithubContentCacheDataSpec(
            'karpathy/char-rnn',
            'master',
            ['data/tinyshakespeare/input.txt'],
        ),
        specs.HttpCacheDataSpec(
            'https://apt.llvm.org/llvm.sh',
        ),
    ]:
        print(spec)
        for _ in range(2):
            print(defaults.default().get(spec))
