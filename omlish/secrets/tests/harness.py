import pytest

from ... import lang
from ...testing.pytest import inject as pti
from ..secrets import Secret
from ..secrets import Secrets


@pti.bind('session')
class HarnessSecrets(Secrets):
    def __init__(self) -> None:
        super().__init__()

    @lang.cached_function
    def _underlying(self) -> Secrets:
        from omdev.home.secrets import load_secrets  # FIXME: manifests? pyproject.toml?
        return load_secrets()

    def _get_raw(self, key: str) -> str:
        return self._underlying()._get_raw(key)  # noqa

    def get_or_skip(self, key: str) -> Secret:
        try:
            return self.get(key)
        except KeyError:
            pytest.skip(f'Required secret: {key}')
