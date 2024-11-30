"""
TODO:
 - use LinuxInterpResolver lol
"""
from ..base import Concern
from ..base import Phase
from ..base import run_in_phase


class VenvConcern(Concern):
    @run_in_phase(Phase.ENV)
    def setup_venv(self) -> None:
        self._d.ush(
            'cd ~/venv',
            f'{self._d.cfg.python_bin} -mvenv {self._d.cfg.app_name}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self._d.cfg.app_name}/bin/python -m ensurepip',
            f'{self._d.cfg.app_name}/bin/python -mpip install --upgrade setuptools pip',

            f'{self._d.cfg.app_name}/bin/python -mpip install -r ~deploy/app/{self._d.cfg.app_name}/{self._d.cfg.requirements_txt}',  # noqa
        )
