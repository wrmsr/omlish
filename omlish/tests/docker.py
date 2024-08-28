from .. import lang
from ..docker import ComposeConfig
from ..testing.pytest import inject as pti


@pti.bind()
class ComposeServices:
    prefix: str = 'omlish-'

    @lang.cached_function
    def compose_config(self) -> ComposeConfig:
        return ComposeConfig(
            self.prefix,
            file_path='docker/compose.yml',
        )
