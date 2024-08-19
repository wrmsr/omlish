import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import DeployConcern
from .base import FsDir
from .base import FsItem


class RepoDeployConcern(DeployConcern['RepoDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        url: str
        revision: str = 'master'
        init_submodules: bool = False

    @cached_nullary
    def repo_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'repos', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.repo_dir())]

    def run(self) -> None:
        rd = self.repo_dir()
        self._deploy.runtime().make_dirs(rd)

        self._deploy.runtime().sh(
            f'cd {rd}',
            'git init',
            f'git remote add origin {self._config.url}',
            f'git fetch --depth 1 origin {self._config.revision}',
            'git checkout FETCH_HEAD',
            *([
                'git submodule update --init',
            ] if self._config.init_submodules else []),
        )
