from ... import lang
from ...testing.pytest import inject as pti
from ..compose import ComposeConfig


@pti.bind()
class ComposeServices:
    prefix: str = 'omlish-'

    @lang.cached_function
    def compose_config(self) -> ComposeConfig:
        return ComposeConfig(
            self.prefix,
            file_path='docker/compose.yml',
        )
