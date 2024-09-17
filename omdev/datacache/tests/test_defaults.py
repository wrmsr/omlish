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
            'https://github.com/DOsinga/deep_learning_cookbook',
            rev='04f56a7fe11e16c19ec6269bc5a138efdcb522a7',
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
