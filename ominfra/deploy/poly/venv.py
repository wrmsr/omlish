import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import DeployConcern
from .base import FsDir
from .base import FsItem
from .repo import RepoDeployConcern


class VenvDeployConcern(DeployConcern['VenvDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        interp_version: str
        requirements_txt: str = 'requirements.txt'

    @cached_nullary
    def venv_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'venvs', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.venv_dir())]

    @cached_nullary
    def exe(self) -> str:
        return os.path.join(self.venv_dir(), 'bin', 'python')

    def run(self) -> None:
        rd = self._deploy.concern(RepoDeployConcern).repo_dir()

        vd = self.venv_dir()
        self._deploy.runtime().make_dirs(vd)
        l, r = os.path.split(vd)

        # FIXME: lol
        py_exe = 'python3'

        self._deploy.runtime().sh(
            f'cd {l}',
            f'{py_exe} -mvenv {r}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self.exe()} -m ensurepip',
            f'{self.exe()} -mpip install --upgrade setuptools pip',

            f'{self.exe()} -mpip install -r {rd}/{self._config.requirements_txt}',  # noqa
        )
