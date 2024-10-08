import os.path

import pytest
import yaml

from ... import lang
from ...testing.pytest import inject as pti
from ..secrets import MappingSecrets
from ..secrets import Secret
from ..secrets import Secrets


@pti.bind('session')
class HarnessSecrets(Secrets):
    def __init__(self):
        super().__init__()

    @lang.cached_function
    def _underlying(self) -> Secrets:
        if not os.path.isfile(sec_file := os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')):
            return MappingSecrets({})

        dct: dict[str, Secret] = {}
        with open(sec_file) as f:
            for k, v in yaml.safe_load(f).items():
                if isinstance(v, str):
                    dct[k] = Secret(key=k, value=v)

        return MappingSecrets(dct)

    def _get_raw(self, key: str) -> str:
        return self._underlying()._get_raw(key)  # noqa

    def get_or_skip(self, key: str) -> Secret:
        try:
            return self.get(key)
        except KeyError:
            pytest.skip(f'Required secret: {key}')
