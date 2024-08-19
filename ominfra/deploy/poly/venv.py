import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import Concern
from .base import FsDir
from .base import FsItem
from .repo import RepoConcern


class VenvConcern(Concern['VenvConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(Concern.Config):
        interp_version: str
        requirements_txt: str = 'requirements.txt'

    @cached_nullary
    def venv_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'venvs', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.venv_dir())]

    def run(self) -> None:
        rd = self._deploy.concern(RepoConcern).repo_dir()

        vd = self.venv_dir()
        self._deploy.runtime().makedirs(vd)
        l, r = os.path.split(vd)

        py_exe = 'python3'
        v_exe = os.path.join(vd, 'bin', 'python')

        self._deploy.runtime().sh(
            f'cd {l}',
            f'{py_exe} -mvenv {r}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{v_exe} -m ensurepip',
            f'{v_exe} -mpip install --upgrade setuptools pip',

            f'{v_exe} -mpip install -r {rd}/{self._config.requirements_txt}',  # noqa
        )
