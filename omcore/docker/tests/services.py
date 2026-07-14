import dataclasses as dc
import typing as ta

from ... import lang
from ...testing.pytest import inject as pti
from ..compose import ComposeConfig


Prefix = ta.NewType('Prefix', str)
DEFAULT_PREFIX = Prefix('omlish-')

DEFAULT_CONFIG_FILE_PATH = 'docker/compose.yml'


@pti.bind()
@dc.dataclass(frozen=True, kw_only=True)
class ComposeServices:
    prefix: Prefix = DEFAULT_PREFIX

    config_file_path: str = DEFAULT_CONFIG_FILE_PATH

    @lang.cached_function
    def config(self) -> ComposeConfig:
        return ComposeConfig(
            self.prefix,
            file_path=self.config_file_path,
        )
