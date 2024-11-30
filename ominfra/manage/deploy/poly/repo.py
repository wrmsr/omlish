import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import DeployConcern
from .base import FsDir
from .base import FsItem
from .base import Runtime
from .configs import DeployConcernConfig


class RepoDeployConcern(DeployConcern['RepoDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        url: str
        revision: str = 'master'
        init_submodules: bool = False

    @cached_nullary
    def repo_dir(self) -> str:
        return os.path.join(self._deploy.site.config.root_dir, 'repos', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.repo_dir())]

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(self.repo_dir())

        runtime.sh(
            f'cd {self.repo_dir()}',
            'git init',
            f'git remote add origin {self._config.url}',
            f'git fetch --depth 1 origin {self._config.revision}',
            'git checkout FETCH_HEAD',
            *([
                'git submodule update --init',
            ] if self._config.init_submodules else []),
        )
