import os.path
import typing as ta

import yaml

from ...testing.pytest import inject as pti
from ..secrets import Secrets
from ..secrets import Secret
from ..secrets import MappingSecrets


TestingSecrets = ta.NewType('TestingSecrets', Secrets)


@pti.bind('session')
def provide_testing_secrets() -> TestingSecrets:
    if not os.path.isfile(sec_file := os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')):
        return ta.cast(TestingSecrets, MappingSecrets({}))

    dct: dict[str, Secret] = {}
    with open(sec_file) as f:
        for k, v in yaml.safe_load(f).items():
            if isinstance(v, str):
                dct[k] = Secret(key=k, value=v)

    return ta.cast(TestingSecrets, MappingSecrets(dct))
