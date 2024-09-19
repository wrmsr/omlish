import os.path

import pytest

from .. import actions
from .. import defaults
from .. import specs


@pytest.mark.online
def test_default():
    from omlish import logs

    logs.configure_standard_logging('INFO')

    #

    for spec in [
        specs.GitSpec(
            'https://github.com/DOsinga/deep_learning_cookbook',
            rev='04f56a7fe11e16c19ec6269bc5a138efdcb522a7',
            subtrees=['data/wp_movies_10k.ndjson'],
        ),
        specs.GithubContentSpec(
            'karpathy/char-rnn',
            'master',
            ['data/tinyshakespeare/input.txt'],
        ),
        specs.UrlSpec(
            'https://apt.llvm.org/llvm.sh',
        ),
        specs.UrlSpec(
            os.path.join('file://' + os.path.join(os.path.dirname(__file__), 'ziptest.tar.gz')),
            actions=[
                actions.ExtractAction(['ziptest.tar.gz']),
            ],
        ),
    ]:
        print(spec)
        for _ in range(2):
            print(defaults.default().get(spec))
