from .. import lang
from ..docker import ComposeConfig
from ..testing.pytest import inject as pti


@pti.bind()
class ComposeServices:
    @lang.cached_function
    def compose_config(self) -> ComposeConfig:
        return ComposeConfig(
            'omlish-',
            file_path='docker/docker-compose.yml',
        )
