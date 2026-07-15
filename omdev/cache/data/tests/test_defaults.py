import os.path

import pytest

from omcore import marshal as msh

from .. import actions
from .. import defaults
from .. import specs


@pytest.mark.online
def test_default():
    from omcore.logs import all as logs

    logs.configure_standard_logging('INFO')

    #

    for spec in [
        specs.GitSpec(
            'https://github.com/wrmsr/om',
            rev='b5afdda1733e406bf98c88cf526b04423e74581e',
            subtrees=('docker/compose.yml',),
        ),
        specs.GithubContentSpec(
            'wrmsr/om',
            'b5afdda1733e406bf98c88cf526b04423e74581e',
            ('README.rst',),
        ),
        specs.UrlSpec(
            'https://google.com/robots.txt',
        ),
        specs.UrlSpec(
            os.path.join('file://' + os.path.join(os.path.dirname(__file__), 'ziptest.tar.gz')),
            actions=(
                actions.ExtractAction(['ziptest.tar.gz']),
            ),
        ),
    ]:
        print(spec)
        for _ in range(2):
            print(defaults.default().get(spec))

        ms = msh.marshal(spec, specs.Spec)
        s2 = msh.unmarshal(ms, specs.Spec)
        assert s2 == spec
